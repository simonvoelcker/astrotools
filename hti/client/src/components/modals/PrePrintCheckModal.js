import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter, Label, Input } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import SpinnerButton from '../panels/SpinnerButton'
import StandardButton from '../panels/StandardButton'

export default class PrePrintCheckModal extends Component {
  constructor (props) {
    super(props)

    this.state = {
      emptyBuildChamber: false,
      checkExtruderT0: false,
      checkExtruderT1: false
    }
  }
  handleChecked (event) {
    let checkItem = event.currentTarget.id
    this.setState({ [checkItem]: !this.state[checkItem] })
  }
  handleStartDisable (store) {
    let extruderSettingsArray = store.extruderSettingsArray

    if (!this.state.emptyBuildChamber) {
      return true
    }
    if (!extruderSettingsArray) {
      return false
    }

    let t0Info = extruderSettingsArray[0]
    if (t0Info && t0Info.active && !this.state.checkExtruderT0) {
      return true
    }
    let t1Info = extruderSettingsArray[1]
    if (t1Info && t1Info.active && !this.state.checkExtruderT1) {
      return true
    }

    return false
  }
  createExtruderCheck = (store, extruderPosition) => {
    if (!store.extruderSettingsArray) {
      return null
    }
    const toolIndex = extruderPosition === 'T0' ? 0 : 1
    const extruderMetaData = store.extruderSettingsArray[toolIndex]

    if (!extruderMetaData || !extruderMetaData.active) {
      return null
    }

    return (
      <div>
        <Input id={'extCheck' + extruderPosition} type='checkbox' defaultChecked={this.state['checkExtruder ' + extruderPosition]} />
        <Label htmlFor={'extCheck' + extruderPosition} style={{ marginTop: '5px' }}>
          <b>{extruderMetaData.variant}</b> installed on <b>{extruderMetaData.position}</b> with <b>{extruderMetaData.material.type}</b> loaded
        </Label>
      </div>
    )
  }
  handleStartJob = (store, mutations) => {
    mutations.startJob()
    mutations.toggleModal('showPrePrintCheckModal')
  }
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal
            isOpen={true}
            toggle={() => mutations.toggleModal('showPrePrintCheckModal')}
            onClosed={() => {
              this.setState({ emptyBuildChamber: false })
              this.setState({ checkExtruderT0: false })
              this.setState({ checkExtruderT1: false })
            }}
            data-cy='PrePrintCheckModal'>
            <ModalHeader>Pre-print checklist</ModalHeader>
            <ModalBody>
              <ul>
                <li id='emptyBuildChamber' onChange={(event) => { (this.handleChecked(event)) }} style={{ padding: '5px 0' }}>
                  <Input id='checkBuildChamber' type='checkbox' defaultChecked={this.state.emptyBuildChamber} />
                  <Label htmlFor='checkBuildChamber' style={{ marginTop: '5px' }}>Check build chamber is empty</Label>
                </li>
                {
                  <div>
                    <li id='checkExtruderT0' style={{ padding: '5px 0' }} onChange={(event) => { (this.handleChecked(event)) }}>
                      { this.createExtruderCheck(store, 'T0') }
                    </li>
                    <li id='checkExtruderT1' style={{ padding: '5px 0' }} onChange={(event) => { (this.handleChecked(event)) }}>
                      { this.createExtruderCheck(store, 'T1') }
                    </li>
                  </div>
                }
              </ul>
            </ModalBody>
            <ModalFooter>
              <SpinnerButton
                datacy='ConfirmStartJob'
                disabled={this.handleStartDisable(store)}
                onClick={() => { this.handleStartJob(store, mutations) }}
                request='startJob'
              >Start Job</SpinnerButton>
              <StandardButton
                datacy='CancelStartJob'
                onClick={() => {mutations.toggleModal('showPrePrintCheckModal')}}
              >Cancel</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

PrePrintCheckModal.contextType = AppContext
