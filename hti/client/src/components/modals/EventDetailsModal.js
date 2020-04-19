import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody } from 'reactstrap'
import { AppContext } from '../../context/AppContext'
import PropTypes from 'prop-types'

export default class EventDetailsModal extends Component {
  render () {
    return (
      <Modal isOpen={this.props.isOpen} toggle={this.props.toggle}>
        <ModalHeader toggle={this.props.toggle}>Event Details</ModalHeader>
        <ModalBody>
          <p><b>Message</b>: {this.props.event.message || '-'}</p>
          <p><b>Severity</b>: {this.props.event.severity || '-'}</p>
          <p><b>Number</b>: {this.props.event.number || '-'}</p>
          <p><b>Help</b>: {this.props.event.helpText || '-'}</p>
          <p><b>Reason</b>: {this.props.event.reasonText || '-'}</p>
          <p><b>Remedy</b>: {this.props.event.remedyText || '-'}</p>
        </ModalBody>
      </Modal>
    )
  }
}

EventDetailsModal.contextType = AppContext

EventDetailsModal.propTypes = {
  event: PropTypes.object,
  isOpen: PropTypes.bool,
  toggle: PropTypes.func,
}
