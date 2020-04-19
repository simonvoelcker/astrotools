import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class AbortJobModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showAbortModal')} data-cy='AbortModal'>
            <ModalHeader>Abort Job</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>Please confirm you that you want to abort the print or continue.</p>
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='primary'
                onClick={() => {
                  mutations.stopJob()
                  mutations.toggleModal('showAbortModal')
                }}
              >Abort Job</StandardButton>
              <StandardButton
                color='secondary'
                onClick={() => mutations.toggleModal('showAbortModal')}
              >Continue Job</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

AbortJobModal.contextType = AppContext
