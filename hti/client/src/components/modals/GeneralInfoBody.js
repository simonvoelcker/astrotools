import React, { Component } from 'react'
import { Row, Col, ModalBody } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatSlicerVersion } from '../../Utils'

export default class GeneralInfoBody extends Component {
  formatHmiVersion = (store) => {
    var line = store.machineInfo.version || 'Unknown'
    if (store.machineInfo.build !== null) {
      line += '-' + store.machineInfo.build
    }
    return line
  }

  formatHmiEnvironment = (store) => {
    var hmiEnvironment = store.machineInfo.hmiEnvironment
    if (hmiEnvironment === undefined) {
      return 'Unknown'
    }

    return (
      <div>
        <span><b>Mode</b>: {hmiEnvironment.mode}<br /></span>
        <span><b>Backend</b>: {hmiEnvironment.plcUrl} {hmiEnvironment.usingSimPrinter.toLowerCase() === 'true' ? '(Simulator)' : ''}<br /></span>
        <span><b>Working Directory</b>: {hmiEnvironment.workingDir}<br /></span>
        <span><b>Mount Directory</b>: {hmiEnvironment.mountDir}<br /></span>
        <span><b>Command Mount Directory</b>: {hmiEnvironment.commandMountDir}<br /></span>
      </div>
    )
  }

  formatExtruderSerialNumbers = (store) => {
    var serials = store.machineInfo.extruderSerialNumbers
    if (serials) {
      return (
        <div>
          <span><b>T0</b>: {serials.t0 || 'Unable to get serial number'}</span><br />
          <span><b>T1</b>: {serials.t1 || 'Unable to get serial number'}</span>
        </div>
      )
    } else {
      return (
        <p>Unable to get serial numbers for extruders</p>
      )
    }
  }

  formatAxisParameters = (store) => {
    var parameters = store.machineInfo.axisParameters
    if (parameters === undefined) {
      return 'Unknown'
    }

    let parametersByAxis = [
      { axis: 'E1', parameters: parameters.t0 },
      { axis: 'E2', parameters: parameters.t1 },
      { axis: 'X', parameters: parameters.x },
      { axis: 'Y', parameters: parameters.y },
      { axis: 'Z', parameters: parameters.z }
    ]

    return (
      <table className='axis-parameters-table'>
        <tbody>
          <tr>
            <td><b>Axis</b></td>
            <td><b>Scaling</b></td>
            <td><b>V_max</b></td>
          </tr>
          {parametersByAxis.map(({ axis, parameters }) =>
            (!parameters.scaling && !parameters.vMax && !parameters.aMax && !parameters.jMax)
              ? <tr key={axis}>
                <td>{axis}</td>
                <td colSpan='4'>No data available. Axis is probably disconnected</td>
              </tr>
              : <tr key={axis}>
                <td>{axis}</td>
                <td>{(parameters.scaling / 10000).toFixed(2)} mm/U</td>
                <td>{(parameters.vMax / 1000).toFixed(0)} mm/min</td>
              </tr>
          )}
        </tbody>
      </table>
    )
  }

  formatFeederCurveSettings = (store) => {
    var settings = store.machineInfo.feederCurveSettings
    if (settings === undefined) {
      return 'Unknown'
    }

    let t0 = settings.t0
    let t1 = settings.t1
    return (
      <div>
        <span><b>T0</b>: <b>Direction</b>={t0.direction.toFixed(0)}, <b>K0</b>={t0.k0.toFixed(4)}, <b>K1</b>={t0.k1.toFixed(4)}, <b>K2</b>={t0.k2.toFixed(4)}</span><br />
        <span><b>T1</b>: <b>Direction</b>={t1.direction.toFixed(0)}, <b>K0</b>={t1.k0.toFixed(4)}, <b>K1</b>={t1.k1.toFixed(4)}, <b>K2</b>={t1.k2.toFixed(4)}</span><br />
      </div>
    )
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <ModalBody style={{ marginBottom: '-20px' }}>
            {store.machineInfo &&
              <div>
                <Row>
                  <Col sm={4}>HMI Version</Col>
                  <Col sm={8}>{this.formatHmiVersion(store)}</Col>
                </Row>
                <Row>
                  <Col sm={4}>HMI Environment</Col>
                  <Col sm={8}>{this.formatHmiEnvironment(store)}</Col>
                </Row>
                <Row>
                  <Col sm={4}>Host Name (GUID)</Col>
                  {/*
                    If network adapter was disconnected, then it will be returned '127.0.0.1' from API.
                    hostName is null means there are exist unexpected status for network adapters.
                  */}
                  <Col sm={8}>{store.machineInfo.hmiEnvironment.hostName || 'Network not available'} ({store.machineInfo.machineGuid})</Col>
                </Row>
                <Row>
                  <Col sm={4}>MongoDB Version</Col>
                  <Col sm={8}>{store.machineInfo.mongodbVersion || 'Unknown'}</Col>
                </Row>
                <Row>
                  <Col sm={4}>Min. Required Blade Version</Col>
                  <Col sm={8}>{store.machineInfo.requiredBladeVersion}</Col>
                </Row>
                <Row>
                  <Col sm={4}>BLADE Version (current job)</Col>
                  <Col sm={8}>{formatSlicerVersion(store)}</Col>
                </Row>
                <Row>
                  <Col sm={4}>Firmware Version</Col>
                  <Col sm={8}>{store.machineInfo.firmwareVersion || 'Unknown'}</Col>
                </Row>
                <Row>
                  <Col sm={4}>FCD Firmware Versions</Col>
                  <Col sm={8}>{store.machineInfo.fcdFirmwareVersions || 'Unknown'}</Col>
                </Row>
                <Row>
                  <Col sm={4}>PLC Serial Number</Col>
                  <Col sm={8}>{store.machineInfo.machineSerialNumber || 'Unknown'}</Col>
                </Row>
                <Row>
                  <Col sm={4}>Extruder Serial Numbers</Col>
                  <Col sm={8}>{this.formatExtruderSerialNumbers(store)}</Col>
                </Row>
                <Row>
                  <Col sm={4}>Axis Parameters</Col>
                  <Col sm={8}>{this.formatAxisParameters(store)}</Col>
                </Row>
                <Row>
                  <Col sm={4}>Feeder Curve Settings</Col>
                  <Col sm={8}>{this.formatFeederCurveSettings(store)}</Col>
                </Row>
              </div>
            }
          </ModalBody>
        )}
      </AppConsumer>
    )
  }
}

GeneralInfoBody.contextType = AppContext
