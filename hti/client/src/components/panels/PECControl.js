import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
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
                <button className='btn' onClick={$backend.stopPECRecording}>STOP</button>
              :
                <button className='btn'
                  disabled={store.pecState.ready}
                  onClick={$backend.startPECRecording}>RECORD</button>
              }

              {store.pecState.replaying ?
                <button className='btn' onClick={$backend.stopPECReplay}>STOP</button>
              :
                <button className='btn'
                  disabled={!store.pecState.ready}
                  onClick={$backend.startPECReplay}>REPLAY</button>
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
