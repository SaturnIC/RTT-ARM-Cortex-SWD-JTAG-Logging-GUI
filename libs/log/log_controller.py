import datetime
import time
import traceback

# Global variables to track the last log filter and highlight change times
lastFilterChangeTime = 0
lastHighlightChangeTime = 0
lastLogGuiFilterUpdateDate = datetime.datetime.now()

# Constants
FILTER_APPLICATION_WAIT_TIME_s = 0.5
GUI_MINIMUM_REFRESH_INTERVAL_s = 0.5

def createUpdateLogTextClosure(logView):
    """
    Create the update log text closure by providing the widgets
    """
    # Store previous data for comparison
    oldFilterString = ""
    lastAppliedFilterString = ""
    filterInputActive = False
    oldHighlightString = ""
    lastAppliedHighlightString = ""
    highlightInputActive = False
    oldRawLogText = ""
    oldFilteredText = ""
    oldTextAfterFreezing = ""
    oldFreezeTextState = False

    def _applyTextFilter(filterStr, unfilteredContent):
        """
        Text log filter function
        """
        filteredLines = ""
        if filterStr:
            for line in unfilteredContent.split('\n'):
                if filterStr.lower() in line.lower():
                    filteredLines += line + '\n'
        else:
            filteredLines = unfilteredContent
        return filteredLines

    def _handleFreezing(rawLogText, newText, freezeTextState):
        """
        Handle freezing of log text
        """
        nonlocal oldTextAfterFreezing
        nonlocal oldFreezeTextState
        if freezeTextState != oldFreezeTextState:
            ### Freeze state changed
            if not freezeTextState:
                # Freeze released
                rawTextAfterFreezing = rawLogText
                newTextF = rawTextAfterFreezing[len(oldTextAfterFreezing):]
                oldFreezeTextState = False
            else:
                # Freeze pressed
                rawTextAfterFreezing = rawLogText
                oldFreezeTextState = True
                oldTextAfterFreezing = rawLogText
                newTextF = newText
        else:
            ### Freeze state stays the same
            if not freezeTextState:
                # Text not frozen
                rawTextAfterFreezing = rawLogText
                newTextF = newText
            else:
                # Text frozen
                rawTextAfterFreezing = oldTextAfterFreezing
                newTextF = ""
        return rawTextAfterFreezing, newTextF

    def _handleFiltering(allText, newText, oldFilteredText, filterString):
        """
        Handle filtering of log text
        """
        nonlocal oldFilterString
        nonlocal lastAppliedFilterString
        nonlocal filterInputActive
        global lastFilterChangeTime

        if filterString == "":
            filteredText = allText
            if oldFilterString != "":
                oldFilterString = ""
                lastAppliedFilterString = ""
                logView.setDefaultColorForFilterLogLinesInput("-FILTER-")
        else:
            current_time = time.time()
            if filterString != oldFilterString:
                oldFilterString = filterString
                lastFilterChangeTime = current_time
                logView.highlightFilterLogLinesInput("-FILTER-")
                filterInputActive = True
            if (lastAppliedFilterString != filterString) and \
               (current_time - lastFilterChangeTime > FILTER_APPLICATION_WAIT_TIME_s):
                lastAppliedFilterString = filterString
                filteredText = _applyTextFilter(lastAppliedFilterString, allText)
                logView.setDefaultColorForFilterLogLinesInput("-FILTER-")
                filterInputActive = False
            else:
                if (filterInputActive and
                    current_time - lastFilterChangeTime > FILTER_APPLICATION_WAIT_TIME_s):
                    logView.setDefaultColorForFilterLogLinesInput("-FILTER-")
                    filterInputActive = False
                if newText:
                    filteredText = oldFilteredText + _applyTextFilter(lastAppliedFilterString, newText)
                else:
                    filteredText = oldFilteredText
        return filteredText

    def _clearLogText():
        nonlocal oldTextAfterFreezing
        filteredText = ""
        oldTextAfterFreezing = ""
        logView.updateLog('')
        return filteredText

    def _highlightText(highlightString, filteredText):
        """
        Highlight matching text in the log
        """
        nonlocal oldHighlightString
        nonlocal oldFilteredText
        nonlocal lastAppliedHighlightString
        nonlocal highlightInputActive
        global lastHighlightChangeTime

        if filteredText == "":
            logView.updateLog("")
            oldFilteredText = filteredText
        else:
            if highlightString == "":
                if highlightString == oldHighlightString:
                    if filteredText != oldFilteredText:
                        logView.updateLog(filteredText)
                        oldFilteredText = filteredText
                else:
                    logView.updateLog(filteredText)
                    oldFilteredText = filteredText
                    logView.setDefaultColorForFilterLogLinesInput("-HIGHLIGHT-")
                    lastAppliedHighlightString = ""
            else:
                current_time = time.time()
                if highlightString != oldHighlightString:
                    lastHighlightChangeTime = current_time
                    logView.highlightFilterLogLinesInput("-HIGHLIGHT-")
                    highlightInputActive = True
                if (lastAppliedHighlightString != highlightString) and \
                   (current_time - lastHighlightChangeTime > FILTER_APPLICATION_WAIT_TIME_s):
                    logView.updateLog('')
                    lastAppliedHighlightString = highlightString
                    logView.colorHighlightedText(filteredText, lastAppliedHighlightString)
                    logView.setDefaultColorForFilterLogLinesInput("-HIGHLIGHT-")
                    highlightInputActive = False
                else:
                    if (highlightInputActive and
                        current_time - lastHighlightChangeTime > FILTER_APPLICATION_WAIT_TIME_s):
                        logView.setDefaultColorForFilterLogLinesInput("-HIGHLIGHT-")
                        highlightInputActive = False
                    if lastAppliedHighlightString == "":
                        logView.updateLog(filteredText)
                        oldFilteredText = filteredText
                    elif len(filteredText) > len(oldFilteredText):
                        if filteredText[:len(oldFilteredText)] == oldFilteredText:
                            newText = filteredText[len(oldFilteredText):]
                            logView.colorHighlightedText(newText, lastAppliedHighlightString)
                        else:
                            logView.colorHighlightedText(filteredText, lastAppliedHighlightString)
                    else:
                        logView.colorHighlightedText(filteredText, lastAppliedHighlightString)
                oldFilteredText = filteredText
        oldHighlightString = highlightString

    def updateLogText(data):
        """
        Main function to update log text with filtering and highlighting
        """
        nonlocal oldRawLogText
        nonlocal oldFilteredText

        currentFreezeState = logView.isLogFrozen()
        rawLogText = oldRawLogText + data
        freezeTextState = currentFreezeState

        rawTextAfterFreezing, newText = _handleFreezing(rawLogText, data, freezeTextState)

        filteredText = _handleFiltering(rawTextAfterFreezing, newText, oldFilteredText, logView.getFilterString())

        if logView.getHighlightString() != "":
            _highlightText(logView.getHighlightString(), filteredText)
        else:
            logView.updateLog(filteredText)

        oldRawLogText = rawTextAfterFreezing
        oldFilteredText = filteredText

    return updateLogText
