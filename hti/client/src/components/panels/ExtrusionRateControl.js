import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import PropTypes from 'prop-types'
import StandardButton from '../panels/StandardButton'
import { Row, Col } from 'reactstrap'

export default class ExtrusionRateControl extends Component {
  render () {
    const minExtrusionRate = 75
    const maxExtrusionRate = 125
    const modalKey = 'showCalibrateExtrusionRateModal' + this.props.tool.toUpperCase()
    const printingOrPaused = this.context.store.printingNow

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div style={{ padding: '10px 0' }}>
            <div>
              <Row style={{ padding: '0.5rem' }}>
                <Col>
                  {this.props.tool.toUpperCase()} Extrusion Rate: {store.extrusionRates[this.props.tool]}%
                </Col>
                <Col>
                  <StandardButton
                    disabled={printingOrPaused || store.pendingRequest !== null}
                    datacy={'CalibrateExtrusionRate' + this.props.tool}
                    onClick={() => { mutations.toggleModal(modalKey) }}>
                      Calibrate
                  </StandardButton>
                </Col>
              </Row>
            </div>
            <div className='slider-holder'>
              <span>{minExtrusionRate}%</span>
              <input
                type='range'
                disabled={store.pendingRequest !== null}
                className='slider'
                min={minExtrusionRate} max={maxExtrusionRate} step='1'
                value={store.extrusionRates[this.props.tool]}
                onChange={(event) => (mutations.setExtrusionRateInStore(this.props.tool, event.target.value))}
                onMouseUp={(event) => (mutations.setExtrusionRate(this.props.tool, event.target.value))}
                onTouchEnd={(event) => (mutations.setExtrusionRate(this.props.tool, event.target.value))} />
              <span>{maxExtrusionRate}%</span>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ExtrusionRateControl.contextType = AppContext

ExtrusionRateControl.propTypes = {
  tool: PropTypes.string
}
