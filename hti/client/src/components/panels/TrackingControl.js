import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Table, Row, Col, Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

// TODOs from 2020-11-07
// capture -> grey out other buttons
// show calibration success and whether it is in progress
// show age of current frame
// when capturing, shouldnt be able to start a sequence, and vice verse
// exposure 10, gain 10000 by default
// auto-start indi server with backend
// investigate 16 sec per frame when 10 is configured
// get sequencing status from BE, same for capturing maybe

export default class TrackingControl extends Component {
  constructor (props) {
    super(props)
    this.state = {
      targetInput: '',
      targetInputStatus: '',
      target: null,
      trackingMode: 'target',
    }
  }

  onChangeTargetInput (event) {
    this.setState({targetInput: event.target.value})
  }

  onSetTarget () {
    let query = this.state.targetInput
    this.setState({targetInputStatus: ''})
    $backend.queryTarget(query).then(response => {
      this.setState({target: response.data})
    }).catch(error => {
      this.setState({targetInputStatus: 'Not found'})
    })
  }

  getTargetProperties (target) {
    const name = target && target.name ? target.name : '-'
    const type = target && target.type ? ' (' + target.type + ')' : ''
    const position = target !== null ? target.ra.toFixed(2) + ', ' + target.dec.toFixed(2) : '-'
    return [
        {key: 'Target name', value: name + type},
        {key: 'Target position', value: position}
    ]
  }

  render () {
    const targetProperties = this.getTargetProperties(this.state.target)

    return (
      <AppConsumer>
        {({ store, mutations }) => (
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
                        <td className="spaced-text">Tracking status:</td>
                        <td className="spaced-text">{store.trackingStatus ? store.trackingStatus.message : '-'}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Row>
                <Row className='row button-row'>
                  <StandardButton
                    disabled={store.imagePath === null || store.tracking || this.state.calibrating}
                    onClick={() => mutations.calibrateImage(this.context)}>CALIBRATE IMAGE</StandardButton>
                  <StandardButton
                    disabled={this.state.target === null || store.tracking || store.imagePosition === null}
                    onClick={$backend.goToTarget}>GO TO TARGET</StandardButton>
                </Row>
                <Row className='row button-row'>
                  { store.tracking ?
                    <StandardButton
                      onClick={$backend.stopTracking}>STOP TRACKING</StandardButton>
                  :
                    <StandardButton
                      disabled={this.state.trackingMode === 'target' && this.state.target === null}
                      onClick={() => {$backend.startTracking(this.state.trackingMode)}}>START TRACKING</StandardButton>
                  }
                  <UncontrolledDropdown>
                    <DropdownToggle caret>MODE: {this.state.trackingMode}</DropdownToggle>
                    <DropdownMenu>
                      <DropdownItem onClick={() => {this.setState({trackingMode: 'target'})}}>Target</DropdownItem>
                      <DropdownItem onClick={() => {this.setState({trackingMode: 'image'})}}>Image</DropdownItem>
                      <DropdownItem onClick={() => {this.setState({trackingMode: 'passive'})}}>Passive</DropdownItem>
                    </DropdownMenu>
                  </UncontrolledDropdown>
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
