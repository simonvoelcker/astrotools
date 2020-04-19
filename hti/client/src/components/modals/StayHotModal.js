import React, { Component } from 'react'
import { Row, Col, Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { formatTemperature, formatTargetTemperature } from '../../Utils.js'
import StandardButton from '../panels/StandardButton'

export default class StayHotModal extends Component {
  constructor (props) {
    super(props)
    this.stayHotTimer = null
    this.state = {
      stayHotSeconds: 5*60
    }
    this.onStayHotTimerFired = this.onStayHotTimerFired.bind(this)
  }
  componentDidMount () {
    this.setState({ stayHotSeconds: 5*60 })
    this.stayHotTimer = setInterval(this.onStayHotTimerFired, 1000)
  }
  componentWillUnmount () {
    if (this.stayHotTimer) {
      clearInterval(this.stayHotTimer)
      this.stayHotTimer = null
    }
  }
  onStayHotTimerFired () {
    if (this.state.stayHotSeconds === 0) {
      this.context.mutations.setTemperature('T0', 0).then(() => {
        this.context.mutations.setTemperature('T1', 0).then(() => {
          this.context.mutations.setTemperature('Bed', 0)
        })
      })
      this.context.mutations.toggleModal('showStayHotModal')
    }

    this.setState((prevState, props) => {
      return { stayHotSeconds: prevState.stayHotSeconds-1 }
    })
  }
  render () {
    // countdown till heating shutdown
    const minutes = Math.floor(this.state.stayHotSeconds/60)
    const seconds = String(this.state.stayHotSeconds % 60).padStart(2, '0')

    const temperatures = this.context.store.temperatures
    const t0 = {
      actual: formatTemperature(temperatures.arExtruderAvg[0]),
      target: formatTargetTemperature(temperatures.arExtruder1),
    }
    const t1 = {
      actual: formatTemperature(temperatures.arExtruderAvg[1]),
      target: formatTargetTemperature(temperatures.arExtruder2),
    }
    const bed = {
      actual: formatTemperature(temperatures.arBed),
      target: formatTargetTemperature(temperatures.rBed),
    }

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <Modal isOpen={true} toggle={() => mutations.toggleModal('showStayHotModal')} data-cy='StayHotModal'>
            <ModalHeader>Job aborted</ModalHeader>
            <ModalBody>
              <p className='spitzmarke'>Heaters will be turned off in</p>
              <h1 style={{ margin: '10px' }}>{minutes}:{seconds}</h1>
              {(t0.target > 0 || t1.target > 0 || bed.target > 0) &&
                <div>
                  <p className='spitzmarke' style={{ margin: '10px 0' }}>Heater status:</p>
                  {t0.target > 0 &&
                    <Row>
                      <Col sm={2}>T0:</Col>
                      <Col sm={10}>{t0.actual}°C ({t0.target + '°C'})</Col>
                    </Row>
                  }
                  {t1.target > 0 &&
                    <Row>
                      <Col sm={2}>T1:</Col>
                      <Col sm={10}>{t1.actual}°C ({t1.target + '°C'})</Col>
                    </Row>
                  }
                  {bed.target > 0 &&
                    <Row>
                      <Col sm={2}>Bed:</Col>
                      <Col sm={10}>{bed.actual}°C ({bed.target + '°C'})</Col>
                    </Row>
                  }
                </div>
              }
            </ModalBody>
            <ModalFooter>
              <StandardButton color='primary' onClick={() => mutations.toggleModal('showStayHotModal')} datacy='KeepItOnButton'>
                Cancel
              </StandardButton>
            </ModalFooter>
          </Modal>
        )}
      </AppConsumer>
    )
  }
}

StayHotModal.contextType = AppContext
