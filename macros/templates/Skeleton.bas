Attribute VB_Name = "Skeleton"
' Skeleton.bas
' CATVBA module equivalent of Skeleton.CATScript. Import into a .catvba project
' (VBA editor, File > Import File). Typed declarations give you IntelliSense.
Option Explicit

Sub CATMain()
    Dim doc As Document
    On Error Resume Next
    Set doc = CATIA.ActiveDocument
    If Err.Number <> 0 Or doc Is Nothing Then
        MsgBox "Open a document first.", vbExclamation, "Skeleton"
        Exit Sub
    End If
    On Error GoTo 0

    Select Case TypeName(doc)
        Case "ProductDocument"
            DoWork doc
        Case Else
            MsgBox "This macro expects a product. Got " & TypeName(doc), vbExclamation, "Skeleton"
    End Select
End Sub

Private Sub DoWork(doc As ProductDocument)
    On Error GoTo Fail
    CATIA.RefreshDisplay = False

    Dim prod As Product
    Set prod = doc.Product
    MsgBox "Active product: " & prod.PartNumber & " with " & prod.Products.Count & " direct children."

    CATIA.RefreshDisplay = True
    Exit Sub
Fail:
    CATIA.RefreshDisplay = True
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, "Skeleton"
End Sub
