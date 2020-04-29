import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
import { Row, Col, Input, Label } from 'reactstrap'

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

  render () {

    const targetString = (this.state.target ?
      this.state.target.name + ' RA=' +
      this.state.target.ra.toFixed(1) + ' Dec=' +
      this.state.target.dec.toFixed(1) : '')

    return (
      <AppConsumer>
        {({ store }) => (
          <div>
            <div className='panel tracking-control-panel'>
              <Row>
                <Col style={{ maxWidth: '350px' }}>
                  <Label style={{width: '80px'}} className='spitzmarke' for='target-input'>Target</Label>
                  <Input style={{width: '230px'}}
                    id='target-input'
                    className='number-input'
                    placeholder="Object name or coordinates"
                    type="text"
                    value={this.state.targetInput}
                    onChange={this.onChangeTargetInput.bind(this)} />
                  <span className="spitzmarke">{this.state.targetInputStatus}</span><br />
                  <span className="spitzmarke">{targetString}</span>
                </Col>
                <Col style={{ maxWidth: '160px' }}>
                  <StandardButton onClick={this.onSetTarget.bind(this)}>SET</StandardButton>
                </Col>
                <Col style={{ maxWidth: '280px' }}>
                  <StandardButton
                    disabled={this.state.target === null}
                    onClick={this.trackTarget.bind(this)}>TRACK TARGET</StandardButton>
                  <StandardButton
                    onClick={this.trackImage.bind(this)}>TRACK IMAGE</StandardButton>
                </Col>
              </Row>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

TrackingControl.contextType = AppContext
