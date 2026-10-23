param(
    [string]$OutputPath = 'output/validacao-ibge-populacao-2025-2026-10-15.json'
)

$municipios = [ordered]@{
    '1501576' = 'Bom Jesus do Tocantins'
    '1501758' = 'Brejo Grande do Araguaia'
    '1502152' = 'Canaã dos Carajás'
    '1502772' = 'Curionópolis'
    '1502954' = 'Eldorado do Carajás'
    '1504208' = 'Marabá'
    '1505494' = 'Palestina do Pará'
    '1505536' = 'Parauapebas'
    '1505635' = 'Piçarra'
    '1507151' = 'São Domingos do Araguaia'
    '1507458' = 'São Geraldo do Araguaia'
    '1507508' = 'São João do Araguaia'
}

$rows = @()
foreach ($entry in $municipios.GetEnumerator()) {
    $code = [string]$entry.Key
    $expected = [string]$entry.Value
    $localitiesUrl = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/$code"
    $seriesUrl = "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2025/variaveis/9324?localidades=N6[$code]"
    $row = [ordered]@{
        ibge_code = $code
        expected_name = $expected
        official_name = $null
        locality_id_matches = $false
        name_matches = $false
        estimate_2025_persons = $null
        series_id_matches = $false
        error = $null
    }
    try {
        $locality = Invoke-RestMethod -Uri $localitiesUrl -TimeoutSec 45
        $row.official_name = [string]$locality.nome
        $row.locality_id_matches = ([string]$locality.id -eq $code)
        $row.name_matches = ($row.official_name -eq $expected)
        $series = Invoke-RestMethod -Uri $seriesUrl -TimeoutSec 60
        $observation = $series[0].resultados[0].series[0]
        $row.series_id_matches = ([string]$observation.localidade.id -eq $code)
        $value = [string]$observation.serie.'2025'
        if ($value -match '^\d+$') {
            $row.estimate_2025_persons = [int64]$value
        } else {
            $row.error = "Non-numeric or absent SIDRA value: $value"
        }
    } catch {
        $row.error = $_.Exception.Message
    }
    $rows += [pscustomobject]$row
}

$result = [ordered]@{
    checked_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    source = 'IBGE Localidades + API de Agregados/SIDRA'
    aggregate = '6579'
    variable = '9324'
    variable_name = 'População residente estimada'
    unit = 'Pessoas'
    period = '2025'
    expected_municipalities = $municipios.Count
    valid_rows = @($rows | Where-Object { $_.locality_id_matches -and $_.name_matches -and $_.series_id_matches -and $null -ne $_.estimate_2025_persons }).Count
    rows = $rows
    note = 'This checks the published estimate, not Censo 2022 population. TLS certificate verification remained enabled.'
}

$directory = Split-Path -Parent $OutputPath
if ($directory) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding utf8
Write-Output "$($result.valid_rows)/$($result.expected_municipalities) valid municipal observations; saved $OutputPath"
if ($result.valid_rows -ne $result.expected_municipalities) {
    $rows | Where-Object { $null -ne $_.error -or -not $_.name_matches -or -not $_.series_id_matches } | Select-Object ibge_code,error | Format-Table
    exit 1
}
