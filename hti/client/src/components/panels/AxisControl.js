import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'

export default class AxisControl extends Component {
  setSpeeds () {
    // this.context.mutations.setSpeeds(this.state.raSpeed, this.state.decSpeed)
  }

  rest () {
    this.context.mutations.setRest()
  }

  stop () {
    this.context.mutations.setSpeeds(0.0, 0.0)
  }

  onChangeRaSpeed (event) {
    // this.setState({raSpeed: event.target.value})
  }

  onChangeDecSpeed (event) {
    // this.setState({decSpeed: event.target.value})
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel axis-control-panel'>
              <div className='settings-column'>
                <div>
                  <Label className='spaced-text' for='ra-speed'>RA</Label>
                  <Input
                    className='number-input'
                    type="number"
                    step="0.001"
                    value={store.axisSpeeds ? store.axisSpeeds.raRevsPerSec : 0}
                    disabled={true}
                    onChange={this.onChangeRaSpeed.bind(this)} />
                </div>
                <div>
                  <Label className='spaced-text' for='dec-speed'>Dec</Label>
                  <Input
                    className='number-input'
                    placeholder="0.0"
                    type="number"
                    step="0.001"
                    value={store.axisSpeeds ? store.axisSpeeds.decRevsPerSec : 0}
                    disabled={true}
                    onChange={this.onChangeDecSpeed.bind(this)} />
                  </div>
              </div>
              <div className='button-column'>
                <StandardButton
                  disabled={true}
                  onClick={this.setSpeeds.bind(this)}>SET</StandardButton>
              </div>
              <div className='button-column'>
                <StandardButton onClick={this.rest.bind(this)}>REST</StandardButton>
                <StandardButton
                  disabled={!store.axisSpeeds || (store.axisSpeeds.raRevsPerSec === 0 && store.axisSpeeds.decRevsPerSec === 0)}
                  onClick={this.stop.bind(this)}>STOP</StandardButton>
              </div>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

AxisControl.contextType = AppContext
