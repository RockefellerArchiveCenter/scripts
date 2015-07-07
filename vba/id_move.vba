Option Explicit

Sub MoveImages()
Dim PicFLD As String, DestFLD As String, picNAME As String
Dim codeRNG As Range, c As Range, picCNT As Long

With ActiveSheet
    If .[A1] <> "ItemNumber" Then
        MsgBox "Please activate the sheet to process before running macro"
        Exit Sub
    End If
    
    PicFLD = "C:\Current\Path\To\My\Pics\"          'remember the final \ in this string
    DestFLD = "D:\Where\I\Want\Them\"               'remember the final \ in this string
    .[M1] = "Pics Moved"                            'setup status column

    Set codeRNG = .Range("A2", .Range("A" & .Rows.Count).End(xlUp))     'cells to process, column A
    For Each c In codeRNG                           'process one at a time
        picNAME = Dir(PicFLD & c.Value & "*")       'find first filename with that code
        Do While Len(picNAME) > 0                   'only continue if a filename is found
            Name PicFLD & picNAME As DestFLD & picNAME      'move the found file
            picCNT = picCNT + 1                     'keep count
            picNAME = Dir                           'get next filename to move
        Loop
        .Range("M" & c.Row).Value = picCNT          'enter results in column M
        picCNT = 0                                  'reset cnt for next code
    Next c                                          'repeat
End With

End Sub
