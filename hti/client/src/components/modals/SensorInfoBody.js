import React, { Component } from 'react'
import { Row, Col, ModalBody } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import {
  INDUCTIVE_SENSOR_RANGE,
  BED_TEMP_WARNING_THRESHOLD,
  BUILD_CHAMBER_TEMP_WARNING_THRESHOLD,
  FILAMENT_CHAMBER_TEMP_WARNING_THRESHOLD,
  EXTRUDER_TEMP_WARNING_THRESHOLD
} from '../../context/Constants'

export default class SensorInfoBody extends Component {

  formatTemperature (temperature, min, max) {
    let formatted = parseFloat(Math.round(temperature * 10) / 10).toFixed(1)
    if (temperature < min || temperature > max) {
      return <span style={{ color: 'red' }}>{formatted}</span>
    }
    if (temperature === 0.0) {
      return <span style={{ color: 'red' }}>N/A</span>
    }
    return formatted
  }

  formatDoorStatus (doorStatus) {
    if (doorStatus) {
      return <span style={{ color: 'red' }}>Open</span>
    } else {
      return <span style={{ color: 'green' }}>Closed</span>
    }
  }

  formatOOFStatus (oofStatus) {
    if (typeof oofStatus === 'boolean') {
      return oofStatus ? <span style={{ color: 'red' }}>Out of Filament</span> : <span style={{ color: 'green' }}>Filament</span>
    } else {
      // "Status not available"
      return oofStatus
    }
  }

  formatInductiveSensorValue (value) {
    if (value >= INDUCTIVE_SENSOR_RANGE) {
      return <span style={{ color: 'red' }}>Out of Range</span>
    } else {
      return value
    }
  }

  render () {
    let store = this.context.store
    let machineStatus = store.selectedMachineStatus

    let temperatures = null
    let temperature_sensor_error = null
    if (machineStatus === null) {
      temperatures = {
        'bed': store.temperatures.arBed,
        'buildChamber': store.temperatures.arBuildChamber,
        't0': store.temperatures.arExtruder[0],
        't1': store.temperatures.arExtruder[1],
        'filamentChamber': store.temperatures.arFilamentChamber,
      }
      temperature_sensor_error = {
        'bed': store.temperatures.bError.arBed,
        'buildChamber': store.temperatures.bError.arBuildChamber,
        't0': store.temperatures.bError.arExtruder[0],
        't1': store.temperatures.bError.arExtruder[1],
        'filamentChamber': store.temperatures.bError.arFilamentChamber,
      }

      machineStatus = {
        '.stInterlocks.bLeft': store.doorStatus.leftOpen,
        '.stInterlocks.bFront': store.doorStatus.frontOpen,
        '.stInterlocks.bRight': store.doorStatus.rightOpen,
        '.stFilamentStatus.arSpool': [[null, store.oofStatus.t0Spool], [null, store.oofStatus.t1Spool]],
        '.stFilamentStatus.arMain': [[null, store.oofStatus.t0Main], [null, store.oofStatus.t1Main]],
        '.stIOLVal.rBedLevelingSensor': store.inductiveSensorStatus.bedLeveling,
        '.stIOLVal.rNozzleCalibSensor': store.inductiveSensorStatus.nozzleCalib,
      }
    } else {
      temperatures = {
        'bed': [
            machineStatus['.HMI.stTempBed.astSensors[1].rValue'],
            machineStatus['.HMI.stTempBed.astSensors[2].rValue'],
        ],
        'buildChamber': [
            machineStatus['.HMI.stTempBuildChamber.astSensors[1].rValue'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[2].rValue'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[3].rValue'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[4].rValue'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[5].rValue'],
        ],
        't0': [
            machineStatus['.HMI.stTempEx0.astSensors[1].rValue'],
            machineStatus['.HMI.stTempEx0.astSensors[2].rValue'],
        ],
        't1': [
            machineStatus['.HMI.stTempEx1.astSensors[1].rValue'],
            machineStatus['.HMI.stTempEx1.astSensors[2].rValue'],
        ],
        'filamentChamber': [
            [
              machineStatus['.HMI.stTempFilamentChamber.astSensors[0].rValue'],
              machineStatus['.HMI.stTempFilamentChamber.astSensors[1].rValue'],
            ],
            [
              machineStatus['.HMI.stTempFilamentChamber.astSensors[2].rValue'],
              machineStatus['.HMI.stTempFilamentChamber.astSensors[3].rValue'],
            ]
        ],
      }
      temperature_sensor_error = {
        'bed': [
            machineStatus['.HMI.stTempBed.astSensors[1].bError'],
            machineStatus['.HMI.stTempBed.astSensors[2].bError'],
        ],
        'buildChamber': [
            machineStatus['.HMI.stTempBuildChamber.astSensors[1].bError'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[2].bError'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[3].bError'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[4].bError'],
            machineStatus['.HMI.stTempBuildChamber.astSensors[5].bError'],
        ],
        't0': [
            machineStatus['.HMI.stTempEx0.astSensors[1].bError'],
            machineStatus['.HMI.stTempEx0.astSensors[2].bError'],
        ],
        't1': [
            machineStatus['.HMI.stTempEx1.astSensors[1].bError'],
            machineStatus['.HMI.stTempEx1.astSensors[2].bError'],
        ],
        'filamentChamber': [
            [
              machineStatus['.HMI.stTempFilamentChamber.astSensors[0].bError'],
              machineStatus['.HMI.stTempFilamentChamber.astSensors[1].bError'],
            ],
            [
              machineStatus['.HMI.stTempFilamentChamber.astSensors[2].bError'],
              machineStatus['.HMI.stTempFilamentChamber.astSensors[3].bError'],
            ]
        ],
      }
    }

    let printerStatusFormatted = store.selectedMachineStatus ? '-' : store.printerStatus.join(', ')

    return (
      <AppConsumer>
        {() => (
          <ModalBody>
            <div className='sensor-info-rows'>
              <Row>
                <Col sm={4}>Bed Temperature</Col>
                {temperatures['bed'].map((value, index) => (
                  <Col sm={1} key={index} style={!temperature_sensor_error['bed'][index]?{}:{color:'red'}}>
                  {!temperature_sensor_error['bed'][index] ? this.formatTemperature(value, 0, BED_TEMP_WARNING_THRESHOLD) : 'Error'}</Col>
                ))}
              </Row>
              <Row>
                <Col sm={4}>Build Chamber Temperature</Col>
                {temperatures['buildChamber'].map((value, index) => (
                  <Col sm={1} key={index} style={!temperature_sensor_error['buildChamber'][index]?{}:{color:'red'}}>
                  {!temperature_sensor_error['buildChamber'][index] ? this.formatTemperature(value, 0, BUILD_CHAMBER_TEMP_WARNING_THRESHOLD) : 'Error'}</Col>
                ))}
              </Row>
              <Row>
                <Col sm={4}>Extruder 1 Temperature</Col>
                {temperatures['t0'].map((value, index) => (
                  <Col sm={1} key={index} style={!temperature_sensor_error['t0'][index]?{}:{color:'red'}}>
                  {!temperature_sensor_error['t0'][index] ? this.formatTemperature(value, 0, EXTRUDER_TEMP_WARNING_THRESHOLD) : 'Error'}</Col>
                ))}
              </Row>
              <Row >
                <Col sm={4}>Extruder 2 Temperature</Col>
                {temperatures['t1'].map((value, index) => (
                  <Col sm={1} key={index} style={!temperature_sensor_error['t1'][index]?{}:{color:'red'}}>
                  {!temperature_sensor_error['t1'][index] ? this.formatTemperature(value, 0, EXTRUDER_TEMP_WARNING_THRESHOLD) : 'Error'}</Col>
                ))}
              </Row>
              <Row>
                <Col sm={4}>Filament Chamber Temperature</Col>
                {temperatures['filamentChamber'][0].map((value, index) => (
                  <Col sm={1} key={index} style={!temperature_sensor_error['filamentChamber'][0][index]?{}:{color:'red'}}>
                  {!temperature_sensor_error['filamentChamber'][0][index] ? this.formatTemperature(value, 0, FILAMENT_CHAMBER_TEMP_WARNING_THRESHOLD) : 'Error'}</Col>
                ))}
                {temperatures['filamentChamber'][1].map((value, index) => (
                  <Col sm={1} key={index} style={!temperature_sensor_error['filamentChamber'][1][index]?{}:{color:'red'}}>
                  {!temperature_sensor_error['filamentChamber'][1][index] ? this.formatTemperature(value, 0, FILAMENT_CHAMBER_TEMP_WARNING_THRESHOLD) : 'Error'}</Col>
                ))}
              </Row>
              <br/>
              <Row>
                <Col sm={4}>Doors</Col>
                <Col sm={2}>Left: {this.formatDoorStatus(machineStatus['.stInterlocks.bLeft'])}</Col>
                <Col sm={2}>Front: {this.formatDoorStatus(machineStatus['.stInterlocks.bFront'])}</Col>
                <Col sm={2}>Right: {this.formatDoorStatus(machineStatus['.stInterlocks.bRight'])}</Col>
              </Row>
              <br/>
              <Row>
                <Col sm={4}>Filament Status (T0)</Col>
                <Col sm={3}>Main: {this.formatOOFStatus(machineStatus['.stFilamentStatus.arMain'][0][1])}</Col>
                <Col sm={3}>Spool: {this.formatOOFStatus(machineStatus['.stFilamentStatus.arSpool'][0][1])}</Col>
              </Row>
              <Row>
                <Col sm={4}>Filament Status (T1)</Col>
                <Col sm={3}>Main: {this.formatOOFStatus(machineStatus['.stFilamentStatus.arMain'][1][1])}</Col>
                <Col sm={3}>Spool: {this.formatOOFStatus(machineStatus['.stFilamentStatus.arSpool'][1][1])}</Col>
              </Row>
              <br/>
              <Row>
                <Col sm={4}>Bed Leveling Ind. Sensor</Col>
                <Col sm={8}>{this.formatInductiveSensorValue(machineStatus['.stIOLVal.rBedLevelingSensor'])}</Col>
              </Row>
              <Row>
                <Col sm={4}>Extruder Calibration Ind. Sensor</Col>
                <Col sm={8}>{this.formatInductiveSensorValue(machineStatus['.stIOLVal.rNozzleCalibSensor'])}</Col>
              </Row>
              <br/>
              <Row>
                <Col sm={4}>Detailed Machine Status</Col>
                <Col sm={8}>{printerStatusFormatted}</Col>
              </Row>
            </div>
          </ModalBody>
        )}
      </AppConsumer>
    )
  }
}

SensorInfoBody.contextType = AppContext
