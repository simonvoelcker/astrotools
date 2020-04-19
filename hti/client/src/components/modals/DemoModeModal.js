import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class DemoModeModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true}
            toggle={() => mutations.toggleModal('showDemoModeModal')}
            data-cy='DemoModeModal'>
            <ModalHeader>DEMO MODE</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>The HMI is running in demo mode. Some functionality is disabled.</p>
            </ModalBody>
            <ModalFooter style={{ display: 'block' }}>
              <StandardButton style={{ marginLeft: '0px' }} onClick={() => { mutations.toggleModal('showDemoModeModal') }}>
                OK
              </StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

DemoModeModal.contextType = AppContext
