# findReplace.vba
Searches a sheet (`Sheet2`) in Excel, for find/replace pairs in columns B and C. Searches column A for matching value in column B, and replaces it with value in column C.

# id_move.vba
Moves files from one directory to another based on matching against a list of IDs in Column A.

## Requirements
Requires Microsoft Excel to work.

## Installation
Navigate to the developer ribbon in Excel. Click on the `Visual Basic` button to open the Microsoft VBA window. Press F7 to open a blank code document. Copy and Past code from id_move.vba into the sheet. Save the sheet to your own computer.

Replace PicFLD and DestFLD with the path to the directories you need to work in.

## Usage
Create a spreadsheet with ItemNumber in the A1 cell. Include any unique identifiers of files that you would like to move in column A below A1. You should not include the file extension (i.e. .pdf).

With the VBA sheet open, hit F5 or Run->Run Sub/UserForm. The script will work and copy any files that match column A.

It may take a while to complete depending on the number of files to move.
