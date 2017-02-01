Sub multiFindNReplace()
    Dim myList, myRange
    Set myList = Sheets("Sheet2").Range("B1:C1000") 'two column range where find/replace pairs are
    Set myRange = Sheets("Sheet2").Range("A1:A54644") 'range to be searched
    For Each cel In myList.Columns(1).Cells
        myRange.Replace what:=cel.Value, replacement:=cel.Offset(0, 1).Value
    Next cel
End Sub
