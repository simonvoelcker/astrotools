import React, { Component } from 'react'
import { Row, Col, Modal, ModalHeader, ModalBody, Input } from 'reactstrap'
import { AppContext } from '../../context/AppContext'
import { formatMemory, formatDuration } from '../../Utils'
import PropTypes from 'prop-types'

export default class JobInfoModal extends Component {
  constructor (props) {
    super(props)

    this.gcodeFile = props.gcodeFile
    this.fileSize = formatMemory(this.gcodeFile.size)
    this.printTime = formatDuration(this.gcodeFile.time)
  }

  render () {
    return (
      <Modal isOpen={this.props.isOpen} toggle={this.props.toggle}>
        <ModalHeader toggle={this.props.toggle}>File Information</ModalHeader>
        <ModalBody>
          <Row className='mb-1'>
            <Col sm={4}>File Name: </Col>
            <Col sm={8}><Input type='text' readOnly value={this.gcodeFile.filename} /></Col>
          </Row>
          <Row className='mb-1'>
            <Col sm={4}>File Path: </Col>
            <Col sm={8}><Input type='text' readOnly value={this.gcodeFile.path} /></Col>
          </Row>
          <Row className='mb-1'>
            <Col sm={4}>File Size: </Col>
            <Col sm={8}><Input type='text' readOnly value={this.fileSize} /></Col>
          </Row>
          <Row className='mb-1'>
            <Col sm={4}>Estimated Time: </Col>
            <Col sm={8}><Input data-cy='PrintTime' type='text' readOnly value={this.printTime} /></Col>
          </Row>
          <Row className='mb-1'>
            <Col sm={4}>Slicer Version: </Col>
            <Col sm={8}><Input data-cy='SlicerVersion' type='text' readOnly value={this.gcodeFile.slicer_version} /></Col>
          </Row>
        </ModalBody>
      </Modal>
    )
  }
}

JobInfoModal.contextType = AppContext // This part is important to access context values

JobInfoModal.propTypes = {
  gcodeFile: PropTypes.object,
  isOpen: PropTypes.bool,
  toggle: PropTypes.func
}
