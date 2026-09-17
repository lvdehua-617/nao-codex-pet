Add-Type -AssemblyName System.Speech
$culture = [System.Globalization.CultureInfo]::GetCultureInfo('zh-CN')
try {
  $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine($culture)
  $recognizer.SetInputToDefaultAudioDevice()
  $recognizer.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
  $result = $recognizer.Recognize([TimeSpan]::FromSeconds(12))
  if ($null -ne $result) { [Console]::OutputEncoding = [Text.Encoding]::UTF8; Write-Output $result.Text }
} finally {
  if ($null -ne $recognizer) { $recognizer.Dispose() }
}
