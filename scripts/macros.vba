Sub InsertAudio_With_Prefix()
    Dim oSlide As Slide
    Dim oShape As Shape
    Dim sPath As String
    Dim sFile As String
    Dim slideIndex As Integer
    Dim audioDuration As Double
    Dim startTime As Double
    Dim filesFoundCount As Integer
    
    ' --- SETTINGS ---
    ' За замовчуванням аудіо шукається у підпапці "audio" поруч із презентацією PPTX.
    ' Якщо потрібно вказати інший шлях, замініть значення sPath (зі зворотним слешем "\" в кінці).
    If ActivePresentation.Path <> "" Then
        sPath = ActivePresentation.Path & "\audio\"
    Else
        sPath = "C:\Path\To\Your\audio\"
    End If
    
    ' File extension
    Const sExt As String = ".wav"
    
    ' File prefix (e.g. for "audio_1.wav", prefix is "audio_")
    Const sPrefix As String = "audio_"
    ' ----------------
    
    filesFoundCount = 0
    
    For Each oSlide In ActivePresentation.Slides
        slideIndex = oSlide.slideIndex
        
        ' Construct filename: Path + "audio_" + SlideNumber + ".wav"
        sFile = sPath & sPrefix & slideIndex & sExt
        
        ' Check if file exists
        If Dir(sFile) <> "" Then
            filesFoundCount = filesFoundCount + 1
            
            ' 1. Insert Audio
            Set oShape = oSlide.Shapes.AddMediaObject2(FileName:=sFile, _
                                                       LinkToFile:=msoFalse, _
                                                       SaveWithDocument:=msoTrue, _
                                                       Left:=10, Top:=10)
            
            ' 2. Wait for codec (fix for 0 duration issue)
            startTime = Timer
            Do While oShape.MediaFormat.Length = 0
                DoEvents
                If Timer - startTime > 2 Then Exit Do
            Loop
            
            ' 3. Configure Playback (Start Auto, Loop False)
            With oShape.AnimationSettings.PlaySettings
                .PlayOnEntry = msoTrue
                .HideWhileNotPlaying = msoTrue
                .LoopUntilStopped = msoFalse
            End With
            
            ' 4. Hard Hide (Move off-screen)
            oShape.Top = -200
            oShape.Left = -200
            
            ' 5. Set Slide Transition Timing
            audioDuration = oShape.MediaFormat.Length
            
            If audioDuration > 0 Then
                With oSlide.SlideShowTransition
                    .AdvanceOnTime = msoTrue
                    ' Duration (ms) to Seconds + 1 second buffer
                    .AdvanceTime = (audioDuration / 1000) + 1
                    .AdvanceOnClick = msoTrue
                End With
            End If
            
        End If
    Next oSlide
    
    ' Final Report
    If filesFoundCount = 0 Then
        MsgBox "No files found!" & vbCrLf & _
               "Looking for: " & sPath & sPrefix & "1" & sExt, vbCritical
    Else
        MsgBox "Success! Audio added to " & filesFoundCount & " slides.", vbInformation
    End If
End Sub









