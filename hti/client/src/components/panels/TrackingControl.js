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
      target: null
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

  trackImage () {
  }

  getTargetProperties (target) {
    return [
        {key: 'Name', value: target && target.name ? target.name : '-'},
        {key: 'Type', value: target && target.type ? target.type : '-'},
        {key: 'Position', value: target !== null ? target.ra.toFixed(2) + ', ' + target.dec.toFixed(2) : '-'},
        {key: 'Constellation', value: target && target.const ? target.const : '-'},
        {key: 'Size', value: target && (target.majAx || target.minAx) ? (target.majAx || '') + 'x' + (target.minAx || '?') : '-'}
    ]
  }

  render () {

    const targetProperties = this.getTargetProperties(this.state.target)

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
                        return <tr>
                          <td className="spaced-text">{targetProperty.key}: </td>
                          <td className="spaced-text">{targetProperty.value}</td>
                        </tr>
                      })}
                    </tbody>
                  </Table>
                </Row>
                <Row className='row tracking-row'>
                  <StandardButton
                    disabled={this.state.target === null}
                    onClick={this.trackTarget.bind(this)}>TRACK TARGET</StandardButton>
                  <StandardButton
                    onClick={this.trackImage.bind(this)}>TRACK IMAGE</StandardButton>
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
