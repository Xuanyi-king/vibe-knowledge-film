# 媒体产物下载与维护

[assets.json](../evidence/assets.json)列出实际URL、字节数和SHA256。两部36秒片原字节在历史commit中保留；当前树只追踪两部1–2MB短验证片和约0.5MB FLAC独听，避免再复制约39MB长片。

本轮实际尝试同仓库Release，创建API可用但附件端点返回401 Bad credentials，失败发布未保留。Git/API写入不等于uploads端点可用。没有绕过运行时凭据，也没有发布到其他网站。之后有可用上传凭据时可从清单下载后用正常`gh release create`再迁移。

Windows PowerShell下载并校验（在仓库根目录）：

```powershell
$Manifest = Get-Content evidence/assets.json -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force ..\vk-media | Out-Null
foreach ($Item in $Manifest.PSObject.Properties) {
    $Target = Join-Path ..\vk-media $Item.Name
    Invoke-WebRequest -Uri $Item.Value.url -OutFile $Target
    $Actual = (Get-FileHash -Algorithm SHA256 $Target).Hash.ToLowerInvariant()
    if ($Actual -ne $Item.Value.sha256) { throw "SHA256 mismatch: $($Item.Name)" }
}
Start-Process ..\vk-media\resonance-final.mp4
Start-Process ..\vk-media\resonance-sfx.flac
```

FLAC是WAV的无损PCM压缩，不是新的混音版本；合音时仍使用本地生成的WAV。源混音与独听轨在mastering前，最终MP4含FFmpeg总线响度处理，音量有意不同。数据检测不替代主观听音。

没有Windows主机，此下载脚本未原生实测。当前分支后续仍可能调整媒体，审查时以清单hash核对；历史两部片的URL已固定到commit。

当前Linux环境已实际下载清单全部7个URL，均HTTP200且字节数/SHA256一致；[下载验证记录](../evidence/revision/downloads.json)。三个FLAC也已解码与原WAV逐样本比对，PCM完全一致。
