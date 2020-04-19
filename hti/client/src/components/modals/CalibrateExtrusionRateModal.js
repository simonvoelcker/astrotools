import React, { Component } from 'react'
import { Row, Col, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatTemperature, formatTargetTemperature } from '../../Utils.js'
import SpinnerButton from '../panels/SpinnerButton'
import PropTypes from 'prop-types'
import StandardButton from '../panels/StandardButton'

export default class CalibrateExtrusionRateModal extends Component {
  constructor () {
    super()
    this.minExtrusionRate = 75
    this.maxExtrusionRate = 125
    this.state = {
      lastExtrusionRate: 100.0,
      extrusionRate: 100.0,
      extrusionAmount: 300.0
    }
  }

  extrudeRequested (extrudeCommand) {
    this.setState((prevState) => {
      return {
        lastExtrusionRate: prevState.extrusionRate,
        extrusionAmount: 300.0
      }
    })
    this.context.mutations.runCommand(extrudeCommand)
  }

  adjustExtrusionRate (amount) {
    const newAmount = this.state.extrusionAmount + amount
    const newRate = this.state.lastExtrusionRate * 300 / newAmount
    if (this.minExtrusionRate < newRate && newRate < this.maxExtrusionRate) {
      this.setState({
        extrusionRate: newRate,
        extrusionAmount: newAmount
      })
    }
  }

  applyChanges () {
    const finalExtrusionRate = Math.round(this.state.extrusionRate)
    this.context.mutations.setExtrusionRate(this.props.tool, finalExtrusionRate)
  }

  render () {
    let store = this.context.store
    const toolName = this.props.tool.toUpperCase()
    const modalKey = 'showCalibrateExtrusionRateModal' + toolName

    const temperatures = store.temperatures
    const toolIndex = (this.props.tool === 't0' ? 0 : 1)
    const actualTemp = formatTemperature(temperatures.arExtruderAvg[toolIndex])
    const targetTemp = this.props.tool === 't0' ? temperatures.arExtruder1 : temperatures.arExtruder2
    const commandSuffix = this.props.tool === 't0' ? 'Ext1' : 'Ext2'
    const extrudeCommand = store.hmiCommands['prm' + commandSuffix]

    let isOOF = this.props.tool === 't0' ? store.oofStatus.t0Main : store.oofStatus.t1Main

    let temperatureOn = this.props.tool === 't0' ? '240.0' : '200.0'

    let toolInfoLine = toolName
    if (store.extruderSettingsArray) {
      const exInfo = store.extruderSettingsArray[toolIndex]
      if (exInfo && exInfo.active) {
        toolInfoLine = exInfo.variant + ' on ' + exInfo.position
        temperatureOn = parseFloat(exInfo.material_temperature).toFixed(1)
      }
    }

    const minExtrusionTemperature = this.props.tool === 't0' ? 230 : 145
    const targetSet = targetTemp >= minExtrusionTemperature
    let temperatureStable = false
    if (this.props.tool === 't0') {
      temperatureStable = temperatures.bErrorState.arExtruder[0].bTempSteadyState
    } else {
      temperatureStable = temperatures.bErrorState.arExtruder[1].bTempSteadyState
    }

    const controlsEnabled =
      store.machineHomed && store.mode !== 'demo' && !store.printingNow && !store.pendingRequest && !store.runningCommand
    const canExtrude = controlsEnabled && !store.doorStatus.doorOpen && !isOOF && targetSet && temperatureStable
    const canHeatUp = controlsEnabled && parseFloat(targetTemp) !== parseFloat(temperatureOn)

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal
            className={'calibrate-extrusion-rate-modal'}
            data-cy='CalibrateExtrusionRateModal'
            backdrop={false}
            isOpen={true}
            toggle={() => mutations.toggleModal(modalKey)}>
            <ModalHeader>Calibrate Extrusion Rate Procedure ({toolInfoLine})</ModalHeader>
            <ModalBody style={{ padding: '0.5rem' }}>
              <Row style={{ padding: '0.5rem' }}>
                <Col>
                  Current Extrusion Rate : <b>{ Math.round(this.state.extrusionRate) }%</b>
                </Col>
                <Col>
                  <StandardButton
                    datacy={'HeatUpButton'}
                    disabled={!canHeatUp}
                    onClick={() => { mutations.setTemperature(toolName, temperatureOn) }}>{temperatureOn}°C</StandardButton><br />
                  <p style={{ textAlign: 'center' }}>Current temperature: <b>{actualTemp}°C</b> ({targetTemp > 0 ? formatTargetTemperature(targetTemp) + '°C' : 'OFF'})&nbsp;&nbsp;{targetSet && temperatureStable ? '✓' : ''}</p>
                </Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                <Col>After heating up the extruder, press <b>EXTRUDE 300mm</b>.</Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                <Col>
                  <SpinnerButton
                    datacy={'Extrude300mmButton'}
                    disabled={!canExtrude}
                    onClick={() => {this.extrudeRequested(extrudeCommand)}}
                    request={extrudeCommand.id}>
                    EXTRUDE 300mm
                  </SpinnerButton>
                </Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                <Col>Please input the actual length of filament that was extruded.</Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                <Col>
                  <div data-cy='AdjustExtrusionRate' style={{ marginBottom: '20px' }}>
                    <div className='increment-container'>
                      <button
                        data-cy='DecreaseButton'
                        disabled={!controlsEnabled}
                        className='btn' style={{ width: '160px' }} onClick={() => { this.adjustExtrusionRate(-0.5) }}>- 0.5 mm</button>
                      <h3> {this.state.extrusionAmount.toFixed(1)} mm </h3>
                      <button
                        data-cy='IncreaseButton'
                        disabled={!controlsEnabled}
                        className='btn' style={{ width: '160px' }} onClick={() => { this.adjustExtrusionRate(+0.5) }}>+ 0.5 mm</button>
                    </div>
                  </div>
                </Col>
              </Row>
            </ModalBody>
            <ModalFooter style={{ borderTop: 'none' }}>
              <StandardButton
                datacy={'CancelButton'}
                onClick={() => mutations.toggleModal(modalKey)}>CANCEL</StandardButton>
              <StandardButton onClick={() => {
                this.applyChanges()
                mutations.toggleModal(modalKey)
              }}>SAVE</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

CalibrateExtrusionRateModal.contextType = AppContext

CalibrateExtrusionRateModal.propTypes = {
  tool: PropTypes.string
}
