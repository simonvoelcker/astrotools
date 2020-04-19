import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatTemperature } from '../../Utils.js'
import StandardButton from '../panels/StandardButton'
import Icon from '../../assets/img/ISO_7010_W017.svg'

export default class UnlockDoorModal extends Component {
  render () {
    let temperatures = this.context.store.temperatures
    const actualBed = formatTemperature(temperatures.arBed)
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showUnlockDoorModal')} data-cy='UnlockDoorModal'>
            <ModalHeader toggle={this.hideRemoveModal}>Hot Surface Warning</ModalHeader>
            <ModalBody>
              <table><tr>
                <td width='100px'>
                  <img src={Icon} alt='icon' width='80%' />
                </td><td>
                  <h3>Print bed temperature at {actualBed} °C<br />Please wear long clothing and gloves.</h3>
                </td>
              </tr></table>
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='danger'
                onClick={() => {
                  mutations.logMessage('hot bed warning dismissed')
                  mutations.toggleModal('showUnlockDoorModal')
                  mutations.unlockDoor()
                }}
              >OK</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

UnlockDoorModal.contextType = AppContext
