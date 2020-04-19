import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppContext } from '../../context/AppContext'
import PropTypes from 'prop-types'
import StandardButton from '../panels/StandardButton'

export default class DeleteJobModal extends Component {
  render () {
    return (
      <Modal isOpen={this.props.isOpen} toggle={this.props.toggle}>
        <ModalHeader toggle={this.hideRemoveModal}>Delete Job</ModalHeader>
        <ModalBody>
          <h3 style={{ margin: '1em 0' }}>Are you sure you want to delete this job?</h3>
          <p>{this.props.filename}</p>
        </ModalBody>
        <ModalFooter>
          <StandardButton
            datacy='DeleteConfirmButton'
            color='danger'
            onClick={() => this.props.removeJob(this.props.filename, this.props.jobId)}
          >Delete</StandardButton>
          <StandardButton
            color='secondary'
            onClick={this.props.toggle}
          >Close</StandardButton>
        </ModalFooter>
      </Modal>
    )
  }
}

DeleteJobModal.contextType = AppContext

DeleteJobModal.propTypes = {
  filename: PropTypes.string,
  jobId: PropTypes.string,
  isOpen: PropTypes.bool,
  toggle: PropTypes.func,
  removeJob: PropTypes.func
}
