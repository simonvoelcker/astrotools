import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class ConfirmHomeModal extends Component {
  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true}
            toggle={() => mutations.toggleModal('showConfirmHomeModal')}
            data-cy='ConfirmHomeModal'>
            <ModalHeader>Safety check</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>Please ensure that the build volume is empty before homing.</p>
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='primary'
                onClick={() => {
                  mutations.startHoming()
                  mutations.toggleModal('showConfirmHomeModal')
                }}>Home Axes</StandardButton>
              <StandardButton
                color='secondary'
                onClick={() => {
                  mutations.toggleModal('showConfirmHomeModal')
                }}>Cancel</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

ConfirmHomeModal.contextType = AppContext
