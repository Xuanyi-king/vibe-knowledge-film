param([switch]$Scene, [switch]$AV, [switch]$SkipTests)
$ErrorActionPreference = 'Stop'
function Invoke-Checked {
    param([string[]]$CommandLine)
    $Program = $CommandLine[0]
    $Arguments = $CommandLine[1..($CommandLine.Count - 1)]
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Failed ($LASTEXITCODE): $($CommandLine -join ' ')" }
}
Push-Location (Join-Path $PSScriptRoot '..')
try {
    foreach ($Name in @('python', 'ffmpeg', 'ffprobe')) { Get-Command $Name -ErrorAction Stop | Out-Null }
    Invoke-Checked -CommandLine @('python', 'engine/get_fonts.py', '--check')
    if ($Scene -or $AV) { Invoke-Checked -CommandLine @('python', 'engine/get_scene_assets.py') }
    if (-not $SkipTests) { Invoke-Checked -CommandLine @('python', '-m', 'unittest', 'discover', '-s', 'tests', '-v') }
    Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/fold_C', '--stills', '24')
    if ($Scene) {
        Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/governor_scene', '--det')
        Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/governor_scene', '--resume', '2')
        Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/governor_scene', '--resume', '2')
        Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/governor_scene', '--events')
        Invoke-Checked -CommandLine @('python', 'engine/audio.py', 'examples/governor_scene')
        Invoke-Checked -CommandLine @('python', 'scripts/check_media.py', 'examples/governor_scene/renders/final.mp4', '--duration', '6')
    }
    if ($AV) {
        Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/resonance', '--det')
        Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/resonance', '--resume', '2')
        Invoke-Checked -CommandLine @('python', 'engine/render.py', 'examples/resonance', '--events')
        Invoke-Checked -CommandLine @('python', 'engine/audio.py', 'examples/resonance', '--stems')
        Invoke-Checked -CommandLine @('python', 'scripts/check_av.py', 'examples/resonance')
        Invoke-Checked -CommandLine @('python', 'scripts/check_visual.py', 'examples/resonance', '--video', 'examples/resonance/renders/final.mp4', '--require', 'mallet-contact', 'felt-contact')
        Invoke-Checked -CommandLine @('python', 'scripts/check_media.py', 'examples/resonance/renders/final.mp4', '--duration', '8', '--loudness')
    }
} finally { Pop-Location }
