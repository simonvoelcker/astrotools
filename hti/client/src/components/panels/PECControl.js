import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import StandardButton from '../panels/StandardButton'
import $backend from '../../backend'
import { Input } from 'reactstrap'


export default class PECControl extends Component {

  onChangeFactor (event) {
    $backend.setPECFactor(event.target.value)
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel pec-control-panel'}>
            <span className='spaced-text'>Periodic Error</span>
            <div className='button-row'>

              {store.pecState.recording ?
                <StandardButton onClick={$backend.stopPECRecording}>STOP</StandardButton>
              :
                <StandardButton
                  disabled={store.pecState.ready}
                  onClick={$backend.startPECRecording}>RECORD</StandardButton>
              }

              {store.pecState.replaying ?
                <StandardButton onClick={$backend.stopPECReplay}>STOP</StandardButton>
              :
                <StandardButton
                  disabled={!store.pecState.ready}
                  onClick={$backend.startPECReplay}>REPLAY</StandardButton>
              }

              <Input type="range" min="-0.01" max="0.01" step="0.0001" className="slider"
                value={store.pecState.factor || 0.0}
                onChange={this.onChangeFactor.bind(this)} />
              <span>{store.pecState.factor}</span>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

PECControl.contextType = AppContext
