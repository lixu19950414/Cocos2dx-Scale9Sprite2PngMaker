# coding=utf-8

"""
	This program can make any size pngs according given plist file.
"""

import plistlib
import os
from PIL import Image
import wx
import sys


# ---------------------------------------------------------
# [TL]0 [T]1 [TR]2
# [L]3 [C]4 [R]5
# [BL]6 [B]7 [BR]8
# ---------------------------------------------------------


ERR_INPUT_WIDTH = 0
ERR_INPUT_HEIGHT = 1
PART_SUFFIX = ["TL", "T", "TR", "L", "C", "R", "BL", "B", "BR"]


def _compose(plistPath, width=0, height=0):
	root = plistlib.readPlist(plistPath)
	textureFileName = root['metadata']['textureFileName']
	realTextureFileName = os.path.splitext(plistPath)[0] + ".png"
	# print realTextureFileName
	picName, form = os.path.splitext(textureFileName)
	frameInfo = [root['frames'][picName + x + form]['frame'] for x in PART_SUFFIX]
	# print frameInfo
	for index, info in enumerate(frameInfo):
		frameInfo[index] = eval(frameInfo[index].replace('{', '(').replace('}', ')'))
	# print frameInfo
	im = Image.open(realTextureFileName)
	regionBox = [frameInfo[x][0] + (frameInfo[x][1][0] + frameInfo[x][0][0], frameInfo[x][1][1] + frameInfo[x][0][1]) for x in range(9)]
	regionLst = [im.crop(x) for x in regionBox]
	# regionLst[1].show()
	if width < regionLst[0].size[0] + regionLst[2].size[0]:
		# print "长度不够"
		return ERR_INPUT_WIDTH
	if height < regionLst[0].size[1] + regionLst[6].size[1]:
		# print "宽度不够"
		return ERR_INPUT_HEIGHT
	newIm = Image.new('RGBA', (width, height), (0, 0, 0, 0))
	# part 4
	point = (frameInfo[0][1][0], frameInfo[0][1][1])
	size = (width - frameInfo[0][1][0] - frameInfo[2][1][0], height - frameInfo[0][1][1] - frameInfo[6][1][1])
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[4].resize(size)
	newIm.paste(tmp, box)
	# part 1
	point = (frameInfo[0][1][0], 0)
	size = (width - frameInfo[0][1][0] - frameInfo[2][1][0], frameInfo[1][1][1])
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[1].resize(size)
	newIm.paste(tmp, box)
	# part 7
	point = (frameInfo[0][1][0], height - frameInfo[6][1][1])
	size = (width - frameInfo[0][1][0] - frameInfo[2][1][0], frameInfo[7][1][1])
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[7].resize(size)
	newIm.paste(tmp, box)
	# part 3
	point = (0, frameInfo[0][1][1])
	size = (frameInfo[3][1][0], height - frameInfo[0][1][1] - frameInfo[6][1][1])
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[3].resize(size)
	newIm.paste(tmp, box)
	# part 5
	point = (width - frameInfo[5][1][0], frameInfo[0][1][1])
	size = (frameInfo[5][1][0], height - frameInfo[0][1][1] - frameInfo[6][1][1])
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[5].resize(size)
	newIm.paste(tmp, box)
	# part 0
	point = (0, 0)
	size = frameInfo[0][1]
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[0]
	newIm.paste(tmp, box)
	# part 2
	point = (width - frameInfo[2][1][0], 0)
	size = frameInfo[2][1]
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[2]
	newIm.paste(tmp, box)
	# part 6
	point = (0, height - frameInfo[6][1][1])
	size = frameInfo[6][1]
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[6]
	newIm.paste(tmp, box)
	# part 8
	point = (width - frameInfo[8][1][0], height - frameInfo[8][1][1])
	size = frameInfo[8][1]
	box = (point[0], point[1], point[0] + size[0], point[1] + size[1])
	tmp = regionLst[8]
	newIm.paste(tmp, box)
	# newIm.show()
	# newIm.save('test.png', "PNG")
	return newIm


class MyFrame(wx.Frame):
	def __init__(self, filename='Select a file.', sizeX=200, sizeY=300):
		wx.Frame.__init__(self, parent=None, title='Scale9Sprite Compose Interface', size=wx.Size(600, 210))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetMaxSize(wx.Size(600, 210))
		self.SetMinSize(wx.Size(600, 210))
		self.Init(filename, sizeX, sizeY)
		self.CenterOnScreen()

	def Init(self, filename, sizeX, sizeY):
		# pMainPanel
		pMainPanel = wx.Panel(self, style=wx.BORDER_THEME)
		self.m_pMainPanel = pMainPanel

		# pBtnBrowse
		pBtnBrowse = wx.Button(
			pMainPanel, label='Browse...',
			pos=wx.Point(0, 0), size=wx.Size(80, 22))
		pBtnBrowse.Bind(wx.EVT_BUTTON, self.onBtnBrowse)
		self.m_pBtnBrowse = pBtnBrowse

		# pBtnMake
		pBtnMake = wx.Button(
			pMainPanel, label='Make',
			pos=wx.Point(480, 56), size=wx.Size(80, 22))
		pBtnMake.Bind(wx.EVT_BUTTON, self.onBtnMake)
		self.m_pBtnMake = pBtnMake

		# pTextCtrl
		pTextCtrl = wx.TextCtrl(
			pMainPanel, -1, filename,
			size=wx.Size(480, 22), pos=wx.Point(90, 5))
		pTextCtrl.m_bChanged = False
		# pTextCtrl.Bind(wx.EVT_TEXT, self.onTextChange)
		self.m_pTextCtrl = pTextCtrl

		# pLabelWidth
		pLabelWidth = wx.StaticText(
			pMainPanel, label="Width", pos=(20, 62))

		# pTextWidth
		pTextCtrl = wx.TextCtrl(
			pMainPanel, -1, str(sizeX),
			size=wx.Size(100, 22), pos=wx.Point(70, 60))
		pTextCtrl.m_bChanged = False
		# pTextCtrl.Bind(wx.EVT_TEXT, self.onTextChange)
		self.m_pTextWidth = pTextCtrl

		# pLabelHeight
		pLabelHeight = wx.StaticText(
			pMainPanel, label="Height", pos=(250, 62))

		# pTextHeight
		pTextCtrl = wx.TextCtrl(
			pMainPanel, -1, str(sizeY),
			size=wx.Size(100, 22), pos=wx.Point(300, 60))
		pTextCtrl.m_bChanged = False
		# pTextCtrl.Bind(wx.EVT_TEXT, self.onTextChange)
		self.m_pTextHeight = pTextCtrl
		
	def onClose(self, event):
		self.Destroy()
		exit()

	def onBtnBrowse(self, event):
		startFolder = ""
		dlg = wx.FileDialog(self, "Choose a file...", startFolder, "", "*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetFilename()
			dirname = dlg.GetDirectory()
			# print filename
			# print dirname
			self.m_pTextCtrl.SetValue(os.path.join(dirname, filename))
		dlg.Destroy()

	def onBtnMake(self, event):
		# print self.m_pTextCtrl.GetValue()
		# print self.m_pTextWidth.GetValue()
		# print self.m_pTextHeight.GetValue()
		try:
			file = self.m_pTextCtrl.GetValue()
			width = int(self.m_pTextWidth.GetValue())
			height = int(self.m_pTextHeight.GetValue())
		except:
			dlg = wx.MessageDialog(self, u"不能获取输入的信息", u"ERROR", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			return
		if not os.path.splitext(file)[1] == ".plist" or not os.path.exists(file):
			dlg = wx.MessageDialog(self, u"给定的文件不正确", u"ERROR", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			return
		startFolder = ""
		dlg = wx.FileDialog(
			self, "Save as...", startFolder, '_' + self.m_pTextWidth.GetValue() + 'x' + self.m_pTextHeight.GetValue() + '.png', "*.*", wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				im = _compose(file, width, height)
			except:
				dlg = wx.MessageDialog(self, u"生成过程中出现未知错误", u"ERROR", wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				return
			if im == ERR_INPUT_WIDTH:
				# print "宽度不够"
				dlg = wx.MessageDialog(self, u"宽度小于最小宽度", u"ERROR", wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				return
			elif im == ERR_INPUT_HEIGHT:
				# print "高度不够"
				dlg = wx.MessageDialog(self, u"高度小于最小高度", u"ERROR", wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				return
			else:
				filename = dlg.GetFilename()
				dirname = dlg.GetDirectory()
				im.save(os.path.join(dirname, filename), "PNG")
		dlg.Destroy()


if __name__ == '__main__':
	app = wx.App()
	if len(sys.argv) > 1:
		frame = MyFrame(*tuple(sys.argv[1:]))
	else:
		frame = MyFrame()
	frame.Show()
	app.MainLoop()


