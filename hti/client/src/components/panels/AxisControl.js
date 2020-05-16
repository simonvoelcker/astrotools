import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Input, Label } from 'reactstrap'

export default class AxisControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
      raSpeed: 0.0,
      decSpeed: 0.0
    }
  }

  getActualSpeeds () {
    this.context.mutations.getSpeeds().then(response => {
      this.setState({
        raSpeed: response.data.ra,
        decSpeed: response.data.dec
      })
    })
  }

  setSpeeds () {
    this.context.mutations.setSpeeds(this.state.raSpeed, this.state.decSpeed).then(() => {
      this.getActualSpeeds()
    })
  }

  rest () {
    this.context.mutations.setRest().then(() => {
      this.getActualSpeeds()
    })
  }

  stop () {
    this.context.mutations.setSpeeds(0.0, 0.0).then(() => {
      this.getActualSpeeds()
    })
  }

  onChangeRaSpeed (event) {
    this.setState({raSpeed: event.target.value})
  }

  onChangeDecSpeed (event) {
    this.setState({decSpeed: event.target.value})
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
                    value={this.state.raSpeed}
                    onChange={this.onChangeRaSpeed.bind(this)} />
                </div>
                <div>
                  <Label className='spaced-text' for='dec-speed'>Dec</Label>
                  <Input
                    className='number-input'
                    placeholder="0.0"
                    type="number"
                    step="0.001"
                    value={this.state.decSpeed}
                    onChange={this.onChangeDecSpeed.bind(this)} />
                  </div>
              </div>
              <div className='button-column'>
                <StandardButton onClick={this.setSpeeds.bind(this)}>SET</StandardButton>
              </div>
              <div className='button-column'>
                <StandardButton onClick={this.rest.bind(this)}>REST</StandardButton>
                <StandardButton
                  disabled={this.state.raSpeed === 0 && this.state.decSpeed === 0}
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
