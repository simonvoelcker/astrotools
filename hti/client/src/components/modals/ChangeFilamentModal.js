import React, { Component } from 'react'
import { Row, Col, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatTemperature, formatTargetTemperature } from '../../Utils.js'
import SpinnerButton from '../panels/SpinnerButton'
import PropTypes from 'prop-types'
import StandardButton from '../panels/StandardButton'

export default class ChangeFilamentModal extends Component {

  constructor (props) {
    super(props)

    this.modalKey = props.tool === 't0' ? 'showChangeFilamentModalT0' : 'showChangeFilamentModalT1'
    this.toolName = props.tool === 't0' ? 'T0' : 'T1'
    this.toolIndex = props.tool === 't0' ? 0 : 1
    this.commandSuffix = props.tool === 't0' ? 'Ext1' : 'Ext2'
  }

  canChangeFilament () {
    // Check conditions that apply to all steps of the change filament procedure
    let store = this.context.store
    if (store.printingNow && !store.isPaused) {
      // actually printing
      return false
    }
    if (!!store.pendingRequest || !!store.runningCommand) {
      return false
    }
    if (store.mode === 'demo') {
      return false
    }
    return true
  }

  canUseExtruder (actualTemp, targetTemp) {
    // Check whether the extruder is ready, i.e. axis is homed and temperature set and stable
    if (!this.context.store.machineHomed) {
      return false
    }

    const temperatures = this.context.store.temperatures
    if (this.props.tool === 't0') {
      return temperatures.bErrorState.arExtruder[0].bTempSteadyState
    } else {
      return temperatures.bErrorState.arExtruder[1].bTempSteadyState
    }
  }

  render () {
    let store = this.context.store

    const temperatures = store.temperatures
    const actualTemp = formatTemperature(temperatures.arExtruderAvg[this.toolIndex])
    const targetTemp = this.props.tool === 't0' ? temperatures.arExtruder1 : temperatures.arExtruder2
    const isOOF = this.props.tool === 't0' ? store.oofStatus.t0Main : store.oofStatus.t1Main

    let temperatureOn = this.props.tool === 't0' ? '240.0' : '200.0'
    let toolInfoLine = this.toolName
    if (store.extruderSettingsArray) {
      const exInfo = store.extruderSettingsArray[this.toolIndex]
      if (exInfo && exInfo.active) {
        toolInfoLine = exInfo.variant + ' on ' + exInfo.position
        temperatureOn = parseFloat(exInfo.material_temperature).toFixed(1)
      }
    }

    const canChangeFilament = this.canChangeFilament()
    const canUseExtruder = this.canUseExtruder(actualTemp, targetTemp)
    const canSetTemperature = canChangeFilament && parseFloat(targetTemp) !== parseFloat(temperatureOn)
    const canUnloadFilament = canChangeFilament && canUseExtruder && !store.doorStatus.doorOpen
    const canLoadFilament = canChangeFilament && canUseExtruder
    const canExtrude = canChangeFilament && canUseExtruder && !store.doorStatus.doorOpen && !isOOF

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal
            className={'change-filament-modal'}
            data-cy='ChangeFilamentModal'
            backdrop={false}
            isOpen={true}
            toggle={() => mutations.toggleModal(this.modalKey)}>
            <ModalHeader>Change Material Procedure ({toolInfoLine})</ModalHeader>
            <ModalBody style={{ padding: '0.5rem' }}>
              <Row style={{ padding: '0.5rem' }}>
                <Col>
                  <b>Step 1:</b> Heat up the extruder and wait for the temperature to stabilize.
                </Col>
                <Col>
                  <StandardButton
                    disabled={!canSetTemperature}
                    onClick={() => { mutations.setTemperature(this.toolName, temperatureOn) }}>
                    {temperatureOn}°C
                  </StandardButton><br />
                  <p style={{ textAlign: 'center' }}>Current temperature: <b>{actualTemp}°C</b> ({targetTemp > 0 ? formatTargetTemperature(targetTemp) + '°C' : 'OFF'})&nbsp;&nbsp;{canUseExtruder ? '✓' : ''}</p>
                </Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                { this.props.tool === 't0' ? (
                  <Col><b>Step 2:</b> Cut filament behind feeder tube, then press <b>UNLOAD FILAMENT</b> button to prepare extruder for new filament.</Col>
                ) : (
                  <Col><b>Step 2:</b> Press <b>UNLOAD FILAMENT</b> button to retract old filament.</Col>
                )}
                <Col>
                  <SpinnerButton
                    disabled={!canUnloadFilament}
                    onClick={() => { mutations.runCommand(store.hmiCommands['unloadFilament' + this.commandSuffix]) }}
                    request={store.hmiCommands['unloadFilament' + this.commandSuffix].id}>
                    UNLOAD FILAMENT
                  </SpinnerButton>
                </Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                <Col><b>Step 3:</b> Press <b>LOAD FILAMENT</b> button and insert new filament into feeder.</Col>
                <Col>
                  <SpinnerButton
                    disabled={!canLoadFilament}
                    onClick={() => { mutations.runCommand(store.hmiCommands['loadFilament' + this.commandSuffix]) }}
                    request={store.hmiCommands['loadFilament' + this.commandSuffix].id}>
                    LOAD FILAMENT
                  </SpinnerButton>
                </Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                <Col><b>Step 4:</b> Press <b>PRIME EXTRUDER</b> button to prime the extruder.</Col>
                <Col>
                  <SpinnerButton
                    disabled={!canExtrude}
                    onClick={() => { mutations.runCommand(store.hmiCommands['prm' + this.commandSuffix]) }}
                    request={store.hmiCommands['prm' + this.commandSuffix].id}>
                    PRIME EXTRUDER
                  </SpinnerButton>
                </Col>
              </Row>
              <Row style={{ padding: '0.5rem' }}>
                <Col>If material was extruded, press <b>CLOSE</b>, otherwise repeat steps as necessary.</Col>
              </Row>
            </ModalBody>
            <ModalFooter style={{ borderTop: 'none' }}>
              <StandardButton onClick={() => mutations.toggleModal(this.modalKey)}>CLOSE</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

ChangeFilamentModal.contextType = AppContext

ChangeFilamentModal.propTypes = {
  tool: PropTypes.string
}
