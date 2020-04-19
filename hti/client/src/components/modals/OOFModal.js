import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class OOFModal extends Component {
  constructor (props) {
    super(props)

    this.state = {
      oofBreadcrumb: 'feedFilament'
    }
  }

  resumePrint () {
    this.context.mutations.toggleModal('showOOFModal')
    this.setState({ oofBreadcrumb: 'feedFilament' })
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showOOFModal')}>
            <ModalHeader>Out of Filament</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>Printer is out of filament. Please perform the change filament procedure on the control page.</p>
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='secondary'
                onClick={() => { mutations.toggleModal('showOOFModal') }}
              >Close</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

OOFModal.contextType = AppContext
