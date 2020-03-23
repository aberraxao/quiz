Option Explicit

Function get_pwd(email As String, theme As String)

    Dim xmlhttp As New MSXML2.XMLHTTP60, myurl As String
    
    On Error GoTo HerrorHandling
    myurl = "http://aberraxao.pythonanywhere.com/sha?user=superuser&pwd=superpwd&email=" & email & "&theme=" & theme
    xmlhttp.Open "GET", myurl, False
    xmlhttp.Send
    
    get_pwd = xmlhttp.responseText
    Exit Function
    
HerrorHandling:
    Debug.Print "SHA http request error: " & Err.Description
End Function

Sub get_themes()
    Dim xmlhttp As New MSXML2.XMLHTTP60, myurl As String, response As Variant, i As Integer, nb_cols As Integer
    
    On Error GoTo HerrorHandling
    myurl = "http://aberraxao.pythonanywhere.com/themes?user=superuser&pwd=superpwd"
    xmlhttp.Open "GET", myurl, False
    xmlhttp.Send
    response = Split(Replace(xmlhttp.responseText, Chr(13), ""), Chr(10))
    
    sh_themes.UsedRange.ClearContents
    nb_cols = UBound(Split(response(i), ",")) + 1
    i = 0
    Do While i <= UBound(response)
        sh_themes.Range("start_themes").Offset(i - 0).Resize(1, nb_cols) = Split(response(i), ",")
        sh_themes.Range("start_themes").Offset(i - 0).Resize(1, nb_cols) = sh_themes.Range("start_themes").Offset(i - 0).Resize(1, nb_cols).Value
        i = i + 1
    Loop
    
    Exit Sub
    
HerrorHandling:
    Debug.Print "Themes http request error: " & Err.Description
End Sub

Sub drag_formulas()
    Dim modo As Integer
    modo = Application.Calculation
    Application.Calculation = xlCalculationAutomatic
    With sh_dash.Range("pwd")
        sh_dash.Range(.Offset(1).Address & ":" & Split(.Offset(1).Address, "$")(1) & .CurrentRegion.Rows.Count).Offset(1).ClearContents
        sh_dash.Range("pwd").Offset(1).Formula = "=get_pwd(" & sh_dash.Range("email").Offset(1).Address(0, 0) & "," & sh_dash.Range("theme").Offset(1).Address(0, 0) & ")"
        If .CurrentRegion.Rows.Count > 2 Then
            .Offset(1).AutoFill Destination:=sh_dash.Range(.Offset(1).Address & ":" & Split(.Offset(1).Address, "$")(1) & .CurrentRegion.Rows.Count), Type:=xlFillDefault
        End If
    End With
    Application.Calculation = modo
End Sub
