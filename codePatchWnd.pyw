#----------------------------------------------------------------------------
# Logicking's CodePatch
#----------------------------------------------------------------------------
# CodePatch is an utility that works in two modes: merging code, and
# creating code patches.
#
# In merge mode it takes files from three folders ('base', 
# 'my' and 'theirs') and put merged files into the result folder. 
# CodePatch also updates binary files, calls external merge
# programs (e.g. WinMerge) to resolve occurred conflicts in text files,
# and writes statistics of performed actions.
# In creating patch mode CodePatch just checks files in 'base' and 'my' folders
# and put files that have been modified in 'my' into the result folder.
#
# CodePatch uses 'pymerge3' (http://code.google.com/p/pymerge3/)
# library to merge two files that have a common ancestor into a single file.
#
#----------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#----------------------------------------------------------------------------
# Copyright (C) 2009 Logicking.com
#----------------------------------------------------------------------------


#----------------------------------------------------------------------------
# File: codePatchWnd.pyw
# Desc: A GUI Shell for CodePatch
#----------------------------------------------------------------------------


import codePatch
import debugWnd

from Tkinter import *
import urllib
import tkFileDialog
import tkFont
import tkMessageBox
import os
import subprocess
import urllib

#using unicode
import sys, locale
reload(sys)
sys.setdefaultencoding(locale.getdefaultlocale()[1])

class Application( Frame ):

    def __init__( self, master ):
        Frame.__init__( self, master )
        self.grid()
        self.create_widgets()

    def create_widgets( self ):

        # Radio buttons for swithcing between modes
        self.current_selection = IntVar()

        ROW = 0

        #separator
        Label(self, text = "                       ").grid(row = ROW, columnspan = 5)

        ROW = ROW + 1
        self.rbttn1 = Radiobutton( self )
        self.rbttn1["text"]     = "Merge code"
        self.rbttn1["variable"] = self.current_selection,
        self.rbttn1["value"]    = 1,
        self.rbttn1["command"]  = self.merge_code_mode
        self.rbttn1.grid( row = ROW, column = 1 )
        
        self.rbttn2 = Radiobutton( self )
        self.rbttn2["text"]     = "Create Patch"
        self.rbttn2["variable"] = self.current_selection,
        self.rbttn2["value"]    = 2,
        self.rbttn2["command"]  = self.create_patch_mode
        self.rbttn2.grid( row = ROW, column = 2)

        #separator
        ROW = ROW + 1
        Label(self, text = " ").grid(row = ROW, columnspan = 5)
        
        editFont = tkFont.Font(size=9)

        # my path
        ROW = ROW + 1
        self.my_path_sign = Label(self, text = "My path: ")
        self.my_path_sign.grid(row = ROW, column = 0, stick = E)
        
        self.my_path_text = Entry(self, width = 40,  font = editFont)
        self.my_path_text.grid(row = ROW, column = 1, columnspan = 3)
        self.my_path_text.insert( 0, codePatch.myCodePath)
        
        self.my_path_bttn = Button( self )
        self.my_path_bttn["text"]= "..."
        self.my_path_bttn["command"] = self.select_my_path
        self.my_path_bttn.grid(row = ROW, column = 4)

        # base path
        ROW = ROW + 1
        self.base_path_sign = Label(self, text = "Base path: " )
        self.base_path_sign.grid(row = ROW, column = 0, stick = E)

        self.base_path_text = Entry(self, width = 40, font = editFont)
        self.base_path_text.grid(row = ROW, column = 1, columnspan = 3)
        self.base_path_text.insert( 0, codePatch.baseCodePath)

        self.base_path_bttn = Button( self )
        self.base_path_bttn["text"]= "..."
        self.base_path_bttn["command"] = self.select_base_path
        self.base_path_bttn.grid(row = ROW, column = 4)

        # their path
        ROW = ROW + 1
        self.their_path_sign = Label(self, text = "Their path: " )
        self.their_path_sign.grid(row = ROW, column = 0, stick = E)
        
        self.their_path_text = Entry(self, width = 40, font = editFont)
        self.their_path_text.grid(row = ROW, column = 1, columnspan = 3)
        self.their_path_text.insert( 0, codePatch.theirCodePath)

        self.their_path_bttn = Button( self )
        self.their_path_bttn["text"]= "..."
        self.their_path_bttn["command"] = self.select_their_path
        self.their_path_bttn.grid(row = ROW, column = 4)

        # result path
        ROW = ROW + 1
        self.result_path_sign = Label(self, text = "Result path: " )
        self.result_path_sign.grid(row = ROW, column = 0, stick = E)
        
        self.result_path_text = Entry(self, width = 40, font = editFont)
        self.result_path_text.grid(row = ROW, column = 1, columnspan = 3)
        self.result_path_text.insert( 0, codePatch.resultCodePath)

        self.result_path_bttn = Button( self )
        self.result_path_bttn["text"]= "..."
        self.result_path_bttn["command"] = self.select_result_path
        self.result_path_bttn.grid(row = ROW, column = 4)
        


        #separator
        ROW = ROW + 1
        Label(self, text = " ").grid(row = ROW, columnspan = 5)

        
        # external diff
        ROW = ROW + 1
        #   check button
        self.use_external_diff_var = IntVar();
        self.use_diff_bttn = Checkbutton( self )
        self.use_diff_bttn["text"]= "Use external program to resolve conflicts (WinMerge)"
        self.use_diff_bttn["command"] = self.use_external_diff
        self.use_diff_bttn["variable"] = self.use_external_diff_var
        self.use_diff_bttn.grid(row = ROW, columnspan = 5)

        self.use_external_diff_var.set(codePatch.useExternalMergeProgram)
        
        #   file name
        ROW = ROW + 1
        self.external_diff_file_sign = Label(self, text = " Program path: " )
        self.external_diff_file_sign.grid(row = ROW, column = 0, stick = E)
        
        self.external_diff_file_text = Entry(self, width = 40, font = editFont)
        self.external_diff_file_text.grid(row = ROW, column = 1, columnspan = 3)
        self.external_diff_file_text.insert( 0, codePatch.mergeProgramPath)

        self.external_diff_path_bttn = Button( self )
        self.external_diff_path_bttn["text"]= "..."
        self.external_diff_path_bttn["command"] = self.select_merge_program_path
        self.external_diff_path_bttn.grid(row = ROW, column = 4)

        #   args
        ROW = ROW + 1
        self.external_diff_args_sign = Label(self, text = " Program args: " )
        self.external_diff_args_sign.grid(row = ROW, column = 0, stick = E)
        
        self.external_diff_args_text = Entry(self, width = 40, font = editFont)
        self.external_diff_args_text.grid(row = ROW, column = 1, columnspan = 3)
        self.external_diff_args_text.insert( 0, codePatch.mergeProgramArgs)

        #separator
        ROW = ROW + 1
        Label(self, text = " ").grid(row = ROW, columnspan = 5)

        ROW = ROW + 1

        # merge bttn
        self.merge_bttn = Button( self )
        self.merge_bttn["text"]= "   PERFORM  MERGE   "
        self.merge_bttn["command"] = self.perform_merge_handler
        self.merge_bttn.grid(row = ROW, columnspan = 5)

        # create patch bttn
        self.create_patch_bttn = Button( self )
        self.create_patch_bttn["text"]= "   CREATE  PATCH   "
        self.create_patch_bttn["command"] = self.create_patch_handler
        self.create_patch_bttn.grid(row = ROW, columnspan = 5)


        #separator
        ROW = ROW + 1
        Label(self, text = " ").grid(row = ROW, columnspan = 5)
        ROW = ROW + 1
        Label(self, text = " ").grid(row = ROW, columnspan = 5)


        # help button
        ROW = ROW + 1
        self.help_bttn = Button( self )
        self.help_bttn["text"]= " How To Use "
        self.help_bttn["command"] = self.help_handler
        self.help_bttn.grid(row = ROW, column = 1, columnspan = 2, stick = E)

        # homepage button
        self.homepage_bttn = Button( self )
        self.homepage_bttn["text"]= " Homepage "
        self.homepage_bttn["command"] = self.homepage_handler
        self.homepage_bttn.grid(row = ROW, column = 3, columnspan = 2, stick = E)


        #separator
        ROW = ROW + 1
        Label(self, text = " ").grid(row = ROW, columnspan = 5)

        #copyright
##        ROW = ROW + 1
##        Label(self, text = " This program is freeware. ").\
##                    grid(row = ROW, columnspan = 5)
        ROW = ROW + 1
        Label(self, text = " Copyright (C) 2009 Logicking.com").\
                    grid(row = ROW, columnspan = 5)




        #starting in "merge" mode
        self.current_selection.set(1)
        self.merge_code_mode()

    def merge_code_mode( self ):
        #show/hide elements
        self.their_path_sign.grid()
        self.their_path_text.grid()
        self.their_path_bttn.grid()
        
        self.use_diff_bttn.grid()
        self.external_diff_file_sign.grid()
        self.external_diff_file_text.grid()
        self.external_diff_path_bttn.grid()
        self.external_diff_args_sign.grid()
        self.external_diff_args_text.grid()

        self.create_patch_bttn.grid_remove()
        self.merge_bttn.grid()

   
    def create_patch_mode( self ):
        #show/hide elements
        self.their_path_sign.grid_remove()
        self.their_path_text.grid_remove()
        self.their_path_bttn.grid_remove()

        self.use_diff_bttn.grid_remove()
        self.external_diff_file_sign.grid_remove()
        self.external_diff_file_text.grid_remove()
        self.external_diff_path_bttn.grid_remove()
        self.external_diff_args_sign.grid_remove()
        self.external_diff_args_text.grid_remove()

        self.merge_bttn.grid_remove()
        self.create_patch_bttn.grid()

    def select_dir( self, text_elem, title ):
        initialDir = text_elem.get()
        dirSelected = tkFileDialog.askdirectory(\
                    title = "Choose location for " + title, \
                    initialdir = initialDir)
        if dirSelected != "" and dirSelected != None:
            dirSelected = dirSelected.replace('/', '\\')
            text_elem.delete( 0, END )
            text_elem.insert( 0, dirSelected )

    def select_my_path( self ):
            self.select_dir(self.my_path_text, "'my' code path")

    def select_base_path( self ):
            self.select_dir(self.base_path_text, "'base' code path")
        
    def select_result_path( self ):
        self.select_dir(self.result_path_text, "'result' code path")

    def select_their_path( self ):
        self.select_dir(self.their_path_text, "'their' code path")


    def select_merge_program_path( self ):
        fileSelected = tkFileDialog.askopenfilename(\
                        title = "Choose external merge program", \
                        filetypes = [("executables","*.exe"), ("allfiles","*")])
        if fileSelected != "" and fileSelected != None:
            fileSelected = fileSelected.replace('/', '\\')
            self.external_diff_file_text.delete( 0, END )
            self.external_diff_file_text.insert( 0, fileSelected )

    def use_external_diff( self ):
        if self.use_external_diff_var:
            self.external_diff_file_text["state"] = NORMAL
        else:
            self.external_diff_file_text["state"] = DISABLED

    def perform_merge_handler( self ):
        self.apply_values()
        result, msg = codePatch.checkDirs()
        if not result:
            tkMessageBox.showinfo( title = "Can't perfrom merge", message = msg )
        else:        
            codePatch.performPatch()
 
    def create_patch_handler( self ):
        self.apply_values()
        result, msg = codePatch.checkDirs(False)
        if not result:
            tkMessageBox.showinfo( title = "Can't create patch", message = msg )
        else:        
            codePatch.createPatch()

    def apply_values( self ):
        codePatch.myCodePath = self.my_path_text.get()
        codePatch.baseCodePath = self.base_path_text.get()
        codePatch.theirCodePath = self.their_path_text.get()
        codePatch.resultCodePath = self.result_path_text.get()

        codePatch.useExternalMergeProgram = self.use_external_diff_var.get() \
                                            and True or False
        codePatch.mergeProgramPath = self.external_diff_file_text.get()
        codePatch.mergeProgramArgs = self.external_diff_args_text.get()

    def homepage_handler( self ):
        subprocess.Popen("codePatch.url", shell=True)
                
    def help_handler( self ):
        subprocess.Popen("codePatch.htm", shell=True)

    
#------------------------------------------------------------------------------
# Script entry point...
#------------------------------------------------------------------------------

def handlerClose():
    debugWnd.Restore_all()
    debugWnd.Dbg_kill_topwin()
    root.destroy()
    app.quit()
    

def create_center_window(w, h):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.resizable(width=FALSE, height=FALSE)


if __name__ == '__main__':

    root = Tk()

    codePatch.readCfg()
    
    root.title("Logicking's CodePatch")
    root.protocol("WM_DELETE_WINDOW", handlerClose)

    create_center_window(400, 400)
        
    app = Application(root)

    debugWnd.Take_all()
    
    root.mainloop()

    
    codePatch.saveCfg()
