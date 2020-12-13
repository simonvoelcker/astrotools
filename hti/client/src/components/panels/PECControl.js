import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import StandardButton from '../panels/StandardButton'
// import $backend from '../../backend'
import { Input } from 'reactstrap'


export default class PECControl extends Component {
  constructor(props) {
    super(props)

    this.state = {
      factor: 0.0,
    }
  }

  onChangeFactor (event) {
    this.setState({factor: event.target.value})
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel pec-control-panel'}>
            <span className='spaced-text'>Periodic Error</span>
            <div className='button-row'>
              <StandardButton
                disabled={store.pecState === null || store.pecState.recording}
                onClick={() => {}}>RECORD</StandardButton>
              <StandardButton
                disabled={store.pecState === null || store.pecState.correcting}
                onClick={() => {}}>CORRECT</StandardButton>
              <Input type="range" min="-10" max="10" step="0.1" className="slider"
                value={this.state.factor}
                onChange={this.onChangeFactor.bind(this)} />
              <span>{this.state.factor}</span>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

PECControl.contextType = AppContext
