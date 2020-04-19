import React, { Component } from 'react'
import { Row, Col, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { formatTemperature, formatTargetTemperature } from '../../Utils.js'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'

export default class ResumeJobModal extends Component {
  render () {
    const temperatures = this.context.store.temperatures
    const t0 = {
      actual: formatTemperature(temperatures.arExtruderAvg[0]),
      target: formatTargetTemperature(temperatures.arExtruder1),
      ready: temperatures.bErrorState.arExtruder[0].bTempSteadyState
    }
    const t1 = {
      actual: formatTemperature(temperatures.arExtruderAvg[1]),
      target: formatTargetTemperature(temperatures.arExtruder2),
      ready: temperatures.bErrorState.arExtruder[1].bTempSteadyState
    }
    const bed = {
      actual: formatTemperature(temperatures.arBed),
      target: formatTargetTemperature(temperatures.rBed),
      ready: temperatures.bErrorState.arBed.bTempSteadyState
    }

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showResumeModal')} data-cy='ResumeModal'>
            <ModalHeader>Resuming Job</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>Waiting for temperatures to stabilize.</p>
              <div>
                {t0.target > 0 &&
                  <Row>
                    <Col sm={2}>T0:</Col>
                    <Col sm={10}>{t0.actual}°C ({t0.target + '°C'})&nbsp;&nbsp;{t0.ready ? '✓' :''}</Col>
                  </Row>
                }
                {t1.target > 0 &&
                  <Row>
                    <Col sm={2}>T1:</Col>
                    <Col sm={10}>{t1.actual}°C ({t1.target + '°C'})&nbsp;&nbsp;{t1.ready ? '✓' :''}</Col>
                  </Row>
                }
                {bed.target > 0 &&
                  <Row>
                    <Col sm={2}>Bed:</Col>
                    <Col sm={10}>{bed.actual}°C ({bed.target + '°C'})&nbsp;&nbsp;{bed.ready ? '✓' :''}</Col>
                  </Row>
                }
              </div>
            </ModalBody>
            <ModalFooter>
              <StandardButton
                color='secondary'
                onClick={() => mutations.toggleModal('showResumeModal')}
              >Close</StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

ResumeJobModal.contextType = AppContext
