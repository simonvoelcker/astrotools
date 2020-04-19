import React, { Component } from 'react'
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import PropTypes from 'prop-types'
import XYcalibrationJobsWidget from '../panels/XYcalibrationJobsWidget'
import StandardButton from '../panels/StandardButton'

export default class OffSetModal extends Component {
  componentWillMount () {
    this.context.mutations.updateAxisOffsets()
  }
  render () {
    const { disableOffsetInputs } = this.props
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showOffSetModal')}>
            <ModalHeader>Tool Correction</ModalHeader>
            <ModalBody>
              <div data-cy='AxisOffset' style={{ marginBottom: '20px' }}>
                <div style={{ width: '100%', textAlign: 'center' }}>XY Extruder Offsets</div>
                <div className='increment-container'>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('x', -1) }} disabled={disableOffsetInputs || store.offsetX === null}>-1</button>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('x', -0.1) }} disabled={disableOffsetInputs || store.offsetX === null}>-0.1</button>
                  <div> X offset: {store.offsetX !== null ? store.offsetX.toFixed(1) : 'Unknown'} </div>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('x', +0.1) }} disabled={disableOffsetInputs || !store.offsetX === null}>+0.1</button>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('x', +1) }} disabled={disableOffsetInputs || !store.offsetX === null}>+1</button>
                </div>
                <div className='increment-container'>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('y', -1) }} disabled={disableOffsetInputs || !store.offsetY === null}>-1</button>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('y', -0.1) }} disabled={disableOffsetInputs || !store.offsetY === null}>-0.1</button>
                  <div> Y offset: {store.offsetY !== null ? store.offsetY.toFixed(1) : 'Unknown'} </div>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('y', +0.1) }} disabled={disableOffsetInputs || !store.offsetY === null}>+0.1</button>
                  <button className='btn' style={{ width: '80px' }} onClick={() => { mutations.adjustOffset('y', +1) }} disabled={disableOffsetInputs || !store.offsetY === null}>+1</button>
                </div>
              </div>
              <XYcalibrationJobsWidget />
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='secondary'
                onClick={() => { mutations.toggleModal('showOffSetModal') }}
              >Close</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

OffSetModal.contextType = AppContext

OffSetModal.propTypes = {
  disableOffsetInputs: PropTypes.bool
}
