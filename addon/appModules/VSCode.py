# coding: UTF-8
"""
VSCode enhancements
Copyright 2020 André-Abush Clause and other contributors. Released under GPL.
GitHub: https://github.com/andre9642/NVDA-VSCode/
"""

import api
import appModuleHandler
import braille
import controlTypes
import speech
import ui
from logHandler import log
from scriptHandler import script, getLastScriptRepeatCount


class AppModule(appModuleHandler.AppModule):

	scriptCategory = "VSCode"

	@staticmethod
	def getEditor():
		obj = api.getFocusObject()
		if obj and obj.role == controlTypes.ROLE_EDITABLETEXT and obj.parent and obj.parent.role == controlTypes.ROLE_LANDMARK and "main" in obj.parent.IA2Attributes["xml-roles"]:
			pass
		else:
			while obj and obj.simpleParent and obj.simpleParent.role != controlTypes.ROLE_APPLICATION:
				obj = obj.simpleParent
			if not obj.simpleParent: return None
			obj = obj.simpleParent.simpleFirstChild
		while obj and obj.role == controlTypes.ROLE_LANDMARK:
			if "main" in obj.IA2Attributes["xml-roles"]:
				break
			obj = obj.simpleNext
		if obj.role != controlTypes.ROLE_LANDMARK:
			return None
		obj = obj.simpleFirstChild
		while obj:
			if obj.role == controlTypes.ROLE_EDITABLETEXT and controlTypes.STATE_MULTILINE in obj.states:
				return obj
			obj = obj.simpleNext
		return None

	@script(
		gestures=[
			"kb:NVDA+h",
			"br(baum):b1+b2+b4+b5+b6+b10"
		],
		description=_("Reads the documentation or suggestion if available")
	)
	def script_readDoc(self, gesture):
		obj = self.getEditor()
		if not obj:
			return ui.message(_("Editor not found"))
		obj = obj.simpleNext
		if not obj:
			return ui.message(_("Nothing"))
		else:
			msgs = []
			while obj:
				if obj.role in [controlTypes.ROLE_TOOLTIP, controlTypes.ROLE_STATICTEXT]:
					if obj.role == controlTypes.ROLE_TOOLTIP:
						obj = obj.simpleFirstChild
					if obj.name.strip() and obj.name != '':
						if obj.description:
							msgs.append(f"{obj.name} {obj.description}")
						else:
							msgs.append(obj.name)
				obj = obj.simpleNext
			scriptCount = getLastScriptRepeatCount()
			if scriptCount == 0:
				braille.handler.message("  ".join(msgs))
				for e in msgs:
					speech.speakMessage(
						e, speech.priorities.SpeechPriority.NEXT)
			else:
				ui.browseableMessage('\n'.join(msgs))

	@script(
		gestures=[
			"kb(desktop):NVDA+end",
			"kb(laptop):NVDA+Shift+end",
			"br(baum):b1+b2+b5+b6+b10"
		],
		description=_("Reads the status bar and moves the navigator to it")
	)
	def script_readStatusBar(self, gesture):
		obj = api.getFocusObject()
		while obj and obj.role != controlTypes.ROLE_STATUSBAR and obj.simpleParent and obj.simpleParent.role != controlTypes.ROLE_APPLICATION:
			obj = obj.simpleParent

		while obj:
			if obj.role is controlTypes.ROLE_STATUSBAR:
				msgs = []
				obj = obj.simpleFirstChild
				api.setNavigatorObject(obj)
				while obj:
					msgs.append(obj.name)
					obj = obj.simpleNext
				scriptCount = getLastScriptRepeatCount()
				if scriptCount == 0:
					braille.handler.message("  ".join(msgs))
					for e in msgs:
						speech.speakMessage(
							e, speech.priorities.SpeechPriority.NEXT)
				else:
					ui.browseableMessage('\n'.join(msgs))
				return
			obj = obj.simpleNext
		ui.message(_("Unable to find status bar"))
