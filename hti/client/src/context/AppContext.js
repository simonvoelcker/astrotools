import React, { Component } from 'react'
import config from '../config'
import $backend from '../backend'
import openSocket from 'socket.io-client'
import {
  getTotalProgressFromPrinterState,
  extractMachineStatus,
  parseElapsedTime,
  jobIsStarted
} from '../Utils'
import PropTypes from 'prop-types'
import appState from './AppState'
import { OOF_TXT } from './Constants'

import errorMessages from './RunRequestErrorMessages'
import { arrayMove } from 'react-sortable-hoc'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)
    this.state = appState
    this.runRequestErrorMessages = errorMessages

    this.mutations = {
      showModal: (key) => {
        this.setState({ currentModal: key })
      },
      hideModal: (key) => {
        if (this.state.currentModal === key) {
          this.setState({ currentModal: null })
        }
      },
      toggleModal: (key) => {
        if (this.state.currentModal === key) {
          this.setState({ currentModal: null })
        } else if (this.state.currentModal === null) {
          this.setState({ currentModal: key })
        }
      },
      switchScene: (selectedScene) => {
        this.setState({ selectedScene })
      },
      updateJobQueue: (jobQueue) => {
        this.setState({ jobQueue })
        let currentJob = this.state.jobQueue[0]
        if (currentJob) {
          let stlFile = currentJob.files.find(file => file.extension === '.stl')
          this.setState({ stlFileName: stlFile ? stlFile.filename : null })
          this.mutations.updateExtruderSettings()
        } else {
          this.setState({ stlFileName: null })
        }
      },
      updateFileList: () => {
        $backend.getJobFileList()
          .then(response => {
            const jobList = response.data
            this.mutations.updateJobQueue(jobList)
          }).catch(error => { this._showModal('Error', 'Could not get job file list', error.response) })
      },
      updateDiskInfo: () => {
        $backend.getDiskInfo()
          .then(response => {
            const diskInfo = response.data
            this.setState({ diskInfo: diskInfo })
          }).catch(error => { this._showModal('Error', 'Could not get disk space info', error.response) })
      },
      updateReportList: () => {
        $backend.getJobReports()
          .then(response => {
            const reportList = response.data
            this.setState({ jobReports: reportList })
          }).catch(error => { this._showModal('Error', 'Could not get report list', error.response) })
      },
      updateMachineInfoList: () => {
        $backend.getMachineInfoList()
          .then(response => {
            const machineInfoList = response.data
            this.setState({ machineInfoList: machineInfoList })
          }).catch(error => { this._showModal('Error', 'Could not get machine info list', error.response) })
      },
      showNetworkInfo: (machineInfoId) => {
        $backend.getMachineInfo(machineInfoId)
          .then(response => {
            const networkInfo = response.data.network_info
            this.setState({ networkInfo })
            this.mutations.toggleModal('showNetworkInfoModal')
          }).catch(error => { this._showModal('Error', 'Could not get machine info', error.response) })
      },
      showMachineInfo: (machineInfoId) => {
        if (machineInfoId) {
          $backend.getMachineInfo(machineInfoId)
            .then(response => {
              const machineInfo = response.data.machine_meta_info
              this.setState({ machineInfo })
              const selectedMachineStatus = response.data.machine_status
              this.setState({ selectedMachineStatus })
              this.mutations.toggleModal('showMachineInfoModal')
            }).catch(error => { this._showModal('Error', 'Could not get machine info', error.response) })
        } else {
          $backend.getHmiMetaInfo()
            .then(response => {
              const machineInfo = response.data
              this.setState({ machineInfo })
              const selectedMachineStatus = null
              this.setState({ selectedMachineStatus })
              this.mutations.toggleModal('showMachineInfoModal')
            }).catch(error => { this._showModal('Error', 'Could not get machine info', error.response) })
        }
      },
      getMetaInfo: () => {
        $backend.getHmiMetaInfo()
          .then(response => {
            const machineInfo = response.data
            this.setState({ machineInfo })
            this.setState({ mode: machineInfo.hmiEnvironment.mode })
            let versionInfo = {
              hmiVersion: machineInfo.version,
              hmiBuild: machineInfo.build,
              firmwareVersion: machineInfo.firmwareVersion
            }
            this.setState({ versionInfo })

            if (machineInfo.hmiEnvironment.mode === 'demo') {
              this.mutations.showModal('showDemoModeModal')
            }
          }).catch(error => { this._showModal('Error', 'Could not get HMI meta info', error.response) })
      },
      setTemperature: (tool, temperature) => {
        return this._runRequest('setTemperature', () => {
          return $backend.setTemperature(tool, temperature)
        })
      },
      setExtruders: (extruders) => {
        this.setState((state) => {
          state.machineInfo['extruderTypes'] = extruders
          return {machineInfo: state.machineInfo};
        });
        if (extruders[0].old_type === null)
          this.mutations.setExtruder(extruders[0].serialNumber, extruders[0].type, extruders[0].desc)
        else if (extruders[0].old_type && extruders[0].old_type !== extruders[0].type)
          this.mutations.updateExtruder(extruders[0].serialNumber, extruders[0].type, extruders[0].desc)
        if (extruders[1].old_type === null)
          this.mutations.setExtruder(extruders[1].serialNumber, extruders[1].type, extruders[1].desc)
        else if (extruders[1].old_type && extruders[1].old_type !== extruders[1].type)
          this.mutations.updateExtruder(extruders[1].serialNumber, extruders[1].type, extruders[1].desc)
      },
      setExtruder: (serial_number, extruder_type, desc) => {
        this._runRequest('setExtruder', () => {
          return $backend.setExtruder(serial_number, extruder_type, desc)
        })
      },
      updateExtruder: (serial_number, extruder_type, desc) => {
        this._runRequest('updateExtruder', () => {
          return $backend.updateExtruder(serial_number, extruder_type, desc)
        })
      },
      setExtrusionRate: (tool, extrusionRate) => {
        this._runRequest('setExtrusionRate(' + tool + ')', () => {
          return $backend.setExtrusionRate(tool, extrusionRate)
        })
      },
      moveJob: ({ oldIndex, newIndex }) => {
        let oldJob = this.state.jobQueue[oldIndex]
        let newJob = this.state.jobQueue[newIndex]

        if (jobIsStarted(newJob)) {
          return
        }

        let jobQueueAfterMove = arrayMove(this.state.jobQueue, oldIndex, newIndex)
        this.setState({ jobQueue: jobQueueAfterMove })
        this.mutations.updateJobQueue(jobQueueAfterMove)

        $backend.setJobPosition(oldJob._id, ++newIndex).catch(error => {
          this._showModal('Error', 'Could not reorder job', error.response)
        })
      },
      uploadFile: (formData, configData, onSuccess, onError) => {
        $backend.uploadFile(formData, configData)
          .then((response) => {
            onSuccess()
            if (response.data) {
              // if the response contains something, it is a warning from the upload validation
              this._showModal('Warning', 'The upload raised a warning', response)
            }
          })
          .catch(error => {
            onError()
            this._showModal('Error', 'There was a problem uploading file', error.response)
          })
      },
      removeJob: (jobId) => {
        return $backend.removeJob(jobId).catch(error => {
          this._showModal('Error', 'Could not remove job', error.response)
        })
      },
      startUpdate: () => {
        let updateFile = this.state.jobQueue[0].name
        this._runRequest('startUpdate', () => {
          return $backend.startUpdate(updateFile)
        })
      },
      startJob: () => {
        let jobId = this.state.jobQueue[0]._id
        this._runRequest('startJob', () => {
          return $backend.startJob(jobId)
        })
      },
      loadCalibrationJob: (jobFile, jobName) => {
        $backend.loadControlJob(jobFile, jobName)
          .then(() => {
            this.mutations.toggleModal('showOffSetModal')
            this.setState({ selectedScene: 'SceneInfos' })
          })
          .catch(error => {
            this._showModal('Error', 'There was a problem uploading control job', error.response)
          })
      },
      handleJobStartRequest: () => {
        for (var extruder in OOF_TXT) {
          if (this.state.printerStatus.includes(OOF_TXT[extruder])) {
            this.mutations.showModal('showOOFModal')
            return
          }
        }
        this.mutations.toggleModal('showPrePrintCheckModal')
      },
      stopCommand: () => {
        this._runRequest('stopJob', () => {
          return $backend.stopJob()
        })
      },
      stopJob: () => {
        this._runRequest('stopJob', () => {
          return $backend.stopJob()
        }).then(() => {
          this.mutations.toggleModal('showStayHotModal')
        })
      },
      downloadReportFile: (filename) => {
        // How to download files using axios
        // https://stackoverflow.com/questions/41938718/how-to-download-files-using-axios
        $backend.downloadJobReportFile(filename)
          .then(responseData => {
            const paths = responseData.config.url.split('/')
            const url = window.URL.createObjectURL(new Blob([responseData.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', paths[paths.length - 1])
            document.body.appendChild(link)
            link.click()
            link.remove()
          }).catch(error => { this._showModal('Error', 'Could not download report file', error.response) })
      },
      saveResponseData: (responseData) => {
        const previousPrinterStatus = [...this.state.printerStatus]

        let printerStatus = extractMachineStatus(responseData, this.state.arLocalMachineStates)
        let printingNow = this.mutations.isPrintingNow(printerStatus)
        let doorStatus = this.mutations.extractDoorStatus(responseData)
        let zPos = this.mutations.extractZPosition(responseData)
        let temperatures = responseData['temperatures']
        let oofStatus = this.mutations.extractOOFStatus(responseData)
        let inductiveSensorStatus = this.mutations.extractInductiveSensor(responseData)
        let isPaused = responseData['.arJobMan[1].stPauseResume.bActive']
        let machineHomed = responseData['.stMachineStatus.bHomed']
        let runningCommand = this.mutations.getRunningCommand(responseData)
        let printProgress = responseData['printing_progress']
        let isHeatingUp = responseData['.stCh01M.M202'] || responseData['.stCh01M.M212'] || responseData['.stCh01M.M222']

        this.setState(runningCommand === this.state.runningCommand ? null : { runningCommand })
        this.setState(previousPrinterStatus === printerStatus ? null : { printerStatus })
        this.setState(zPos)
        this.setState(printingNow)
        this.setState(doorStatus)
        this.setState(oofStatus)
        this.setState(inductiveSensorStatus)
        this.setState({ temperatures })
        this.setState(machineHomed === this.state.machineHomed ? null : { machineHomed })
        this.setState(isPaused === this.state.isPaused ? null : { isPaused })
        this.setState(this.state.InitialDataLoaded ? null : { InitialDataLoaded: true })
        if (this.mutations.eStopTriggered()) {
          this.mutations.hideModal('showChangeFilamentModalT0')
          this.mutations.hideModal('showChangeFilamentModalT1')
          this.mutations.hideModal('showCalibrateExtrusionRateModalT0')
          this.mutations.hideModal('showCalibrateExtrusionRateModalT1')
        }
        if (!this.state.runningCommand) {
          this.setState(printProgress === this.state.printProgress ? null : { printProgress })
          let totalPrintProgress = getTotalProgressFromPrinterState(this.state.printerStatus, printProgress)
          this.setState(totalPrintProgress === this.state.totalPrintProgress ? null : { totalPrintProgress })
        }
        this.setState({ isHeatingUp })

        this.mutations.extractFlowRates(responseData)
        this.mutations.checkForOOFStatusChange(previousPrinterStatus, printerStatus)
        this.mutations.updateElapsedPrintTime(responseData)
      },
      extractFlowRates: (responseData) => {
        const receivedExtrusionRateT0 = Math.round(responseData['NC.CplPermVariable,@EX1_FACTOR'] * 100)
        const receivedExtrusionRateT1 = Math.round(responseData['NC.CplPermVariable,@EX2_FACTOR'] * 100)

        if (!this.state.changingExtrusionRate.t0 && !this.state.changingExtrusionRate.t1) {
          this.setState({ extrusionRates: { t0: receivedExtrusionRateT0, t1: receivedExtrusionRateT1 } })
        } else {
          let newValue = this.state.changingExtrusionRate
          if (this.state.changingExtrusionRate.t0 === receivedExtrusionRateT0) {
            newValue.t0 = null
          }
          if (this.state.changingExtrusionRate.t1 === receivedExtrusionRateT1) {
            newValue.t1 = null
          }
          this.setState({ changingExtrusionRate: newValue })
        }
      },
      extractZPosition: (responseData) => {
        let zPos = responseData['.arAxes[3].rPos']
        return (zPos === this.state.zPos) ? null : { zPos }
      },
      isPrintingNow: (printerStatus) => {
        // TODO this is highly confusing. printingNow will be true when commands run, and when a job is paused.
        let printingNow = printerStatus.includes('Job is running') || printerStatus.includes('NC program is running')

        if (printingNow !== this.state.printingNow) {
          if (!printingNow) {
            this.mutations.onPrintStopped()
          }
          return { printingNow }
        }

        return null
      },
      onPrintStopped: () => {
        if (this.state.runningCommand === null) return

        if (this.state.runningCommand.id === 'bedLevelling') {
          this.mutations.getBedMap()
        }
      },
      setUploadFilename: (uploadFilename) => {
        this.setState({ uploadFilename })
      },
      setUploadPercentage: (uploadPercentage) => {
        this.setState({ uploadPercentage })
      },
      updateElapsedPrintTime: (printerStatus) => {
        if (this.state.runningCommand === null) {
          let elapsedTimeStr = printerStatus['.stMachineStatus.strElapsedTime']
          let elapsedPrintTime = parseElapsedTime(elapsedTimeStr)
          this.setState({ elapsedPrintTime })
        }
      },
      updateLatestElapsedPrintTime: (latestElapsedPrintTime) => {
        this.setState({ latestElapsedPrintTime })
      },
      extractDoorStatus: (responseData) => {
        let doorStatus = {
          doorLocked: responseData['.stInterlocks.bDoorsLocked'],
          leftOpen: !responseData['.stInterlocks.bLeft'],
          frontOpen: !responseData['.stInterlocks.bFront'],
          rightOpen: !responseData['.stInterlocks.bRight'],
          doorOpen: !responseData['.stInterlocks.bFront'] || !responseData['.stInterlocks.bLeft'] || !responseData['.stInterlocks.bRight']
        }

        return (doorStatus === this.state.doorStatus) ? null : { doorStatus }
      },
      extractOOFStatus: (responseData) => {
        let notAvailableMessage = 'Status not available'
        let spoolOOF = responseData['.stFilamentStatus.arSpool']
        let mainOOF = responseData['.stFilamentStatus.arMain']

        let oofStatus = {
          t0Spool: spoolOOF ? spoolOOF[0][1] : notAvailableMessage,
          t0Main: mainOOF ? mainOOF[0][1] : notAvailableMessage,
          t1Spool: spoolOOF ? spoolOOF[1][1] : notAvailableMessage,
          t1Main: mainOOF ? mainOOF[1][1] : notAvailableMessage
        }

        return (oofStatus === this.state.oofStatus) ? null : { oofStatus }
      },
      extractInductiveSensor: (responseData) => {
        let inductiveSensorStatus = {
          bedLeveling: responseData['.stIOLVal.rBedLevelingSensor'],
          nozzleCalib: responseData['.stIOLVal.rNozzleCalibSensor']
        }
        return (inductiveSensorStatus === this.state.inductiveSensorStatus) ? null : { inductiveSensorStatus }
      },
      checkForOOFStatusChange: (previousPrinterStatus, printerStatus) => {
        for (var extruder in OOF_TXT) {
          if (!previousPrinterStatus.includes(OOF_TXT[extruder]) && printerStatus.includes(OOF_TXT[extruder])) {
            this.mutations.showModal('showOOFModal')
            return
          }
        }
      },
      saveJobQueue: (responseData) => {
        this.mutations.updateJobQueue(responseData)
        this.mutations.updateDiskInfo()
      },
      updateExtruderSettings: () => {
        let jobFile = this.state.jobQueue[0]
        if (!jobFile) return

        let gcodeFile = jobFile.files.find(file => {
          return file.extension === '.gcode'
        })

        let extruderSettingsArray = gcodeFile ? gcodeFile.extruder_data : null
        this.setState({ extruderSettingsArray })

        let machineSettings = gcodeFile ? gcodeFile.machine_data : null
        this.setState({ machineSettings })
      },
      saveJobReport: (responseData) => {
        this.setState({ jobReports: responseData })
      },
      lockDoor: () => {
        this._runRequest('lockDoor', () => {
          return $backend.setDoorLock(true)
        })
      },
      unlockDoor: () => {
        this._runRequest('unlockDoor', () => {
          return $backend.setDoorLock(false)
        })
      },
      startHoming: () => {
        this._runRequest('homePrinter', () => {
          return $backend.homePrinter()
        })
      },
      resetPrinter: () => {
        this._runRequest('resetPrinter', () => {
          return $backend.resetPrinter()
        })
      },
      getRunningCommand: (responseData) => {
        let commandID = responseData['running_command_id']
        return commandID ? this.state.hmiCommands[commandID] : null
      },
      updateInstalledCommands: () => {
        $backend.getInstalledCommands().then((response) => {
          const installedCommands = response.data
          let customCommands = installedCommands.filter(command => command.customButton)
          this.setState({ customCommands })

          let hmiCommands = { ...this.state.hmiCommands }
          let receivedHmiCommands = installedCommands.filter(command => command.hmiButton)
          for (var command of receivedHmiCommands) {
            let commandID = command.id.trim()
            if (commandID in hmiCommands) {
              hmiCommands[commandID] = command
            }
          }
          this.setState({ hmiCommands })
          let missingCommands = Object.keys(hmiCommands).filter(key => hmiCommands[key] === undefined)
          if (missingCommands.length > 0) {
            this.setState({ missingCommands })
            this.setState({ showMissingCommands: true })
          }
        }).catch(error => { this._showModal('Error', 'Could not get installed commands', error.response) })
      },
      runCommand: (command) => {
        this._runRequest(command.id, () => {
          return $backend.runCommand(command)
        })
      },
      setExtrusionRateInStore: (tool, extrusionRate) => {
        let newValue = this.state.changingExtrusionRate
        newValue[tool] = Number(extrusionRate)
        this.setState({ changingExtrusionRate: newValue })
        this.setState((prevState, props) => {
          let extrusionRates = { ...prevState.extrusionRates }
          extrusionRates[tool] = extrusionRate
          return { extrusionRates }
        })
      },
      getBedMap: () => {
        $backend.getBedMap().then((response) => {
          let bedMapValues = response.data.bedMapValues
          let bedMapPoints = bedMapValues.bedMapping
          let bedMapDelta = bedMapValues.deltaValue

          this.setState({ bedMapPoints })
          this.setState({ bedMapDelta })
        }).catch(error => {
          this._showModal('Error', 'Could not retrieve bed mapping values', error.response)
        })
      },
      moveAxis: (direction, distance) => {
        this._runRequest('moveAxis', () => {
          return $backend.moveAxis(direction, distance)
        })
      },
      eStopTriggered: () => {
        return this.state.printerStatus.includes('E-Stop has been triggered')
      },
      logMessage: (message) => {
        $backend.logMessage(message).catch(() => {
          this._showModal('Error', 'Could not create log message', message)
        })
      },
      updateLogMessages: (logMessages) => {
        // check whether events have happened since the last log message update
        let newestKnownLogMessage = this.state.logMessages[0]
        for (var i=0; i<logMessages.length; i++) {
          // note that this works even if newestKnownLogMessage is undefined (empty list)
          if (logMessages[i] === newestKnownLogMessage) {
            break
          }
          if (this._logMessageIsEvent(logMessages[i])) {
            this.setState({ newEventReceived: true })
          }
        }
        this.setState({ logMessages })
      },
      acknowledgeEvents: () => {
        this.setState({ newEventReceived: false })
      },
      pause: () => {
        this._runRequest('pauseJob', () => {
          return $backend.pauseJob()
        })
      },
      resume: () => {
        this._runRequest('resumeJob', () => {
          return $backend.resumeJob()
        }, false).catch(error => {
          if (error.response.status === 504) {
            // custom error handling for timeouts - show a message explaining why resuming take long
            this.mutations.toggleModal('showResumeModal')
          } else {
            // default error handling if it was not a timeout
            this._showModal('Error', this.runRequestErrorMessages['resumeJob'], error.response)
          }
        })
      },
      exitHmi: () => {
        $backend.exitHmi().catch(error => {
          this._showModal('Error', 'Could not exit the HMI', error.response)
        })
      },
      adjustOffset: (axis, amount) => {
        var offsetX = this.state.offsetX
        var offsetY = this.state.offsetY
        if (axis === 'x') {
          offsetX = Math.round((parseFloat(this.state.offsetX) + amount) * 10) / 10
        } else {
          offsetY = Math.round((parseFloat(this.state.offsetY) + amount) * 10) / 10
        }
        let newOffsets = { target: 'T1', offsetX: offsetX, offsetY: offsetY }
        $backend.setDCorrections(newOffsets).then((response) => {
          const printerDCorrections = response.data
          for (var i = 0; i < printerDCorrections.D.length; i++) {
            if (printerDCorrections.D[i].Com.indexOf('T1') !== -1) {
              const offsetX = Number(printerDCorrections.D[i].L1)
              const offsetY = Number(printerDCorrections.D[i].L2)
              this.setState({ offsetX })
              this.setState({ offsetY })
              break
            }
          }
        }).catch(error => {
          this._showModal('Error', 'Could not set D-Correction values', error.response)
          this.mutations.updateAxisOffsets()
        })
      },
      updateAxisOffsets: () => {
        $backend.getDCorrections()
          .then(response => {
            const printerDCorrections = response.data
            for (var i = 0; i < printerDCorrections.D.length; i++) {
              if (printerDCorrections.D[i].Com.indexOf('T1') !== -1) {
                const offsetX = Number(printerDCorrections.D[i].L1)
                const offsetY = Number(printerDCorrections.D[i].L2)
                this.setState({ offsetX })
                this.setState({ offsetY })
                break
              }
            }
          }).catch(error => { this._showModal('Error', 'Could not get D-Correction values', error.response) })
      },
      canStartOrResumeJob: () => {
        if (!this.state.machineHomed || this.state.doorStatus.doorOpen) {
          return false
        }
        if (!this.state.extruderSettingsArray) {
          // No extruder metadata available - In dubio pro reo
          return true
        }
        let t0Info = this.state.extruderSettingsArray[0]
        if (t0Info && t0Info.active && (this.state.oofStatus.t0Main || !this.state.temperatures.bTempOkExt1)) {
          // T0 is used in the print, but is OOF or has sensor issues
          return false
        }
        let t1Info = this.state.extruderSettingsArray[1]
        if (t1Info && t1Info.active && (this.state.oofStatus.t1Main || !this.state.temperatures.bTempOkExt2)) {
          // T1 is used in the print, but is OOF
          return false
        }
        // No tool used or all used tools have filament
        return true
      }
    }
  }

  componentDidMount () {
    this.setState({ OPCConnectionChecker: setInterval(this.checkOPCServerConnected.bind(this), 1000) })
  }

  checkOPCServerConnected () {
    $backend.checkConnectedToPrinter().then(response => {
      if (response.data.opcServerStarted) {
        this._onOPCServerConnected()
      }
    }).catch(error => { this._showModal('Error', 'Could not check if opc connected', error.response) })
  }

  // TODO rename things to make this more generic
  // TODO start using it elsewhere, also
  _showModal (title, message, response) {
    let modalInfo = {}
    modalInfo.title = title || 'Error'
    modalInfo.message = message || 'A request failed'

    if (response === undefined) {
      modalInfo.details = 'No details were provided by the server.'
    } else if (response.status === 403) {
      modalInfo.message = 'This request was not allowed by the server.'
      modalInfo.remedy = 'Perform this action on the machine, not remotely.'
    } else {
      let errorData = response.data
      let errorString = (typeof errorData === 'string' || errorData instanceof String) ? errorData : errorData.message

      try {
        // the server response may contain structured data (JSON) with some attributes
        let errorObject = JSON.parse(errorString)
        modalInfo.message = errorObject.message
        modalInfo.details = errorObject.details
        modalInfo.remedy = errorObject.remedy
      } catch (e) {
        modalInfo.details = 'Status code: ' + response.status
      }
    }

    this.setState({genericModalInfo: modalInfo})
    this.mutations.showModal('showGenericInfoModal')
  }

  _runRequest (requestName, requestCallback, handleError=true) {
    // Convenience method to handle requests that should disable controls
    // Parameter requestName: Identifies the request (sets state.pendingRequest).
    // Parameter requestCallback: A callback function which runs the actual request.
    // Parameter handleError: (optional): Whether or not to show an error dialog.

    if (this.state.pendingRequest !== null) {
      this._showModal('Error', 'A request is already pending')
      return Promise.reject('A request is already pending')
    }
    this.setState({ pendingRequest: requestName })
    let promise = requestCallback().then((response) => {
      this.setState({ pendingRequest: null })
      return Promise.resolve(response)
    }).catch((error) => {
      this.setState({ pendingRequest: null })
      if (handleError) {
        this._showModal('Error', this.runRequestErrorMessages[requestName], error.response)
      }
      return Promise.reject(error)
    })
    return promise
  }

  _logMessageIsEvent (logMessage) {
    const eventRegex = /(?<timestamp>.*)\s*-\s*(?<jsonbody>\{.*\})/
    return eventRegex.exec(logMessage) !== null
  }

  _onOPCServerConnected () {
    clearInterval(this.state.OPCConnectionChecker)
    this.setState({ socket: openSocket(config.WEBSOCKET_URL) })
    this._getInitialData()
    this._subscribeToSocketEvents()
    $backend.getLog().catch(error => {
      this._showModal('Error', 'Could trigger log message web socket update', error.response)
    })
  }

  _getInitialData () {
    this.mutations.getMetaInfo()
    this.mutations.updateFileList()
    this.mutations.updateInstalledCommands()
  }

  _subscribeToSocketEvents () {
    this.state.socket.on('update', (data) => {
      this.mutations.saveResponseData(data)
    })
    this.state.socket.on('all-job-file', (data) => {
      this.mutations.saveJobQueue(data)
    })
    this.state.socket.on('all-report-file', (data) => {
      this.mutations.saveJobReport(data)
    })
    this.state.socket.on('status-log', (data) => {
      this.mutations.updateLogMessages(data)
    })
  }

  render () {
    return (
      <AppContext.Provider
        value={{
          store: this.state,
          mutations: this.mutations
        }}
      >
        {this.props.children}
      </AppContext.Provider>
    )
  }
}

AppProvider.propTypes = {
  children: PropTypes.node.isRequired
}

export const AppConsumer = AppContext.Consumer
