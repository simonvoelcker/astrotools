import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Table, Row, Col, Input, Label } from 'reactstrap'

export default class TrackingControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
      targetInput: '',
      targetInputStatus: '',
      target: null,
      calibrating: false
    }
  }

  onChangeTargetInput (event) {
    this.setState({targetInput: event.target.value})
  }

  onSetTarget () {
    let query = this.state.targetInput
    this.setState({targetInputStatus: ''})
    this.context.mutations.queryTarget(query).then(response => {
      this.setState({target: response.data})
    }).catch(error => {
      this.setState({targetInputStatus: 'Not found: ' + query})
    })
  }

  trackTarget () {
  }

  calibrateImage () {
    this.setState({calibrating: true})
    this.context.mutations.calibrateImage(this.context.store.imagePath).then(response => {
      this.setState({calibrating: false})
    }).catch(error => {
      this.setState({calibrating: false})
    })
  }

  getTargetProperties (target) {
    const name = target && target.name ? target.name : '-'
    const type = target && target.type ? ' (' + target.type + ')' : ''
    const position = target !== null ? target.ra.toFixed(2) + ', ' + target.dec.toFixed(2) : '-'
    const size = target && (target.majAx || target.minAx) ? (target.majAx || '') + 'x' + (target.minAx || '?') : '-'
    return [
        {key: 'Name', value: name + type},
        {key: 'Position', value: position},
        {key: 'Size', value: size}
    ]
  }

  render () {
    const targetProperties = this.getTargetProperties(this.state.target)
    let imagePosition = '-'
    if (this.context.store.imagePosition !== null) {
      imagePosition = this.context.store.imagePosition.ra.toFixed(2) + ', ' +
                      this.context.store.imagePosition.dec.toFixed(2)
    }
    let imageRotation = '-'
    if (this.context.store.imageRotation !== null) {
      imageRotation = this.context.store.imageRotation.angle.toFixed(2) + '°'
    }

    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel tracking-control-panel'>
              <span className='spaced-text panel-title'>Tracking Control</span>
              <Col>
                <Row className='row target-select-row'>
                  <Label className='spaced-text' for='target-input'>Target:</Label>
                  <Input
                    id='target-input'
                    className='number-input'
                    placeholder="Object name or coordinates"
                    type="text"
                    value={this.state.targetInput}
                    onChange={this.onChangeTargetInput.bind(this)} />
                  <span className="spaced-text">{this.state.targetInputStatus}</span>
                  <StandardButton onClick={this.onSetTarget.bind(this)}>SET</StandardButton>
                </Row>
                <Row className='row target-display-row'>
                  <Table>
                    <tbody>
                      {targetProperties.map(targetProperty => {
                        return <tr key={targetProperty.key}>
                          <td className="spaced-text">{targetProperty.key}: </td>
                          <td className="spaced-text">{targetProperty.value}</td>
                        </tr>
                      })}
                      <tr>
                        <td className="spaced-text">Image center:</td>
                        <td className="spaced-text">{imagePosition}</td>
                      </tr>
                      <tr>
                        <td className="spaced-text">Image rotation:</td>
                        <td className="spaced-text">{imageRotation}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Row>
                <Row className='row tracking-row'>
                  <StandardButton
                    disabled={this.state.target === null}
                    onClick={this.trackTarget.bind(this)}>TRACK TARGET</StandardButton>
                  <StandardButton
                    disabled={this.state.calibrating}
                    onClick={this.calibrateImage.bind(this)}>CALIBRATE IMAGE</StandardButton>
                </Row>
              </Col>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

TrackingControl.contextType = AppContext
