import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export class EStopModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} data-cy='EStopModal' style={{ maxWidth: '550px' }}>
            <ModalHeader>Safety circuit interrupted</ModalHeader>
            <ModalBody>
              <p className='spitzmarke' style={{ marginBottom: '10px' }}>Please check the following:</p>
              <p>1. Emergency stops are released</p>
              <p>2. Both extruders are connected (turn off machine before connecting)</p>
              <p className='spitzmarke' style={{ marginTop: '10px' }}>If the error persists, contact BigRep support.</p>
            </ModalBody>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}
EStopModal.contextType = AppContext

export class CommandsModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showMissingCommands')}>
            <ModalHeader>Some commands are missing</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>Some Commands used in the HMI are missing. Buttons that use these commands will be disabled.</p>
              {store.missingCommands.map((command, index) => {
                return (
                  <h4 key={index}>{command}</h4>
                )
              })}
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='primary'
                onClick={() => mutations.toggleModal('showMissingCommands')}
              >Close</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}
CommandsModal.contextType = AppContext

export class GenericInfoModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} data-cy='GenericInfoModal'>
            <ModalHeader>{store.genericModalInfo.title}</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>{store.genericModalInfo.message}</p>
              {store.genericModalInfo.details &&
                <p className='spitzmarke' style={{ marginTop: '10px' }}><b>Details:</b> {store.genericModalInfo.details}</p>
              }
              {store.genericModalInfo.remedy &&
                <p className='spitzmarke' style={{ marginTop: '10px' }}><b>Remedy: </b>{store.genericModalInfo.remedy}</p>
              }
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='primary'
                onClick={() => mutations.toggleModal('showGenericInfoModal')}
              >Close</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}
GenericInfoModal.contextType = AppContext

export class WrongFirmwareModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} data-cy='WrongFirmwareModal'>
            <ModalHeader>Update Required</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>HMI not compatible with current Firmware version.</p>
              <p className='spitzmarke'>HMI: {store.machineInfo.version || 'Unknown'}</p>
              <p className='spitzmarke'>Current Firmware: {store.machineInfo.firmwareVersion || 'Unknown'}</p>
              <p className='spitzmarke'>Minimum Required Firmware: {store.machineInfo.requiredFirmwareVersion}</p>
              <p className='spitzmarke'>Please contact BigRep Support.</p>
            </ModalBody>
            <ModalFooter>
              <StandardButton
                className='btn'
                disabled={store.mode === 'demo'}
                onClick={mutations.exitHmi}
              >Exit Hmi
              </StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}
WrongFirmwareModal.contextType = AppContext
