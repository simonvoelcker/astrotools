import React, { Component } from 'react'
import { Label, Input } from 'reactstrap'
import { AppConsumer, AppContext } from '../../appstate'
import StandardButton from '../panels/StandardButton'
import $backend from '../../backend'

export default class GuidingControl extends Component {

  constructor(props) {
    super(props)

    this.state = {
      raEnable: true,
      raRange: 2.0,
      raInvert: true,
      raP: 0.02,
      raI: 0.0,
      raD: 0.0,
      decEnable: true,
      decRange: 20,
      decInvert: true,
      decP: 0.04,
      decI: 0.0,
      decD: 0.0,
    }
  }

  startGuiding () {
    $backend.startGuiding(this.props.camera, this.state)
  }

  stopGuiding () {
    $backend.stopGuiding(this.props.camera)
  }

  render () {
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel guiding-control-panel'}>
            { store.guiding ?
              <StandardButton onClick={this.stopGuiding.bind(this)}>Stop guiding</StandardButton>
            :
              <StandardButton onClick={this.startGuiding.bind(this)}>Start guiding</StandardButton>
            }

            <div className='settings-row'>
              <span className='spaced-text'></span>
              <span className='spaced-text'>RA</span>
              <span className='spaced-text'>Dec</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Enable</Label>
              <input type="checkbox"
                     className="checkbox-input"
                     disabled={store.guiding}
                     checked={this.state.raEnable}
                     onChange={(e) => this.setState({raEnable: e.target.checked})} />
              <input type="checkbox"
                     className="checkbox-input"
                     disabled={store.guiding}
                     checked={this.state.decEnable}
                     onChange={(e) => this.setState({decEnable: e.target.checked})} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Range (°/h)</Label>
              <Input id='ra-range' className='number-input' type="number" step="0.1"
                     disabled={store.guiding}
                     value={this.state.raRange}
                     onChange={(e) => this.setState({raRange: e.target.value})} />
              <Input id='dec-range' className='number-input' type="number" step="0.1"
                     disabled={store.guiding}
                     value={this.state.decRange}
                     onChange={(e) => this.setState({decRange: e.target.value})} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Invert</Label>
              <input type="checkbox"
                     className="checkbox-input"
                     disabled={store.guiding}
                     checked={this.state.raInvert}
                     onChange={(e) => this.setState({raInvert: e.target.checked})} />
              <input type="checkbox"
                     className="checkbox-input"
                     disabled={store.guiding}
                     checked={this.state.decInvert}
                     onChange={(e) => this.setState({decInvert: e.target.checked})} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>P-Term</Label>
              <Input id='ra-p' className='number-input' type="number" step="0.01"
                     disabled={store.guiding}
                     value={this.state.raP}
                     onChange={(e) => this.setState({raP: e.target.value})} />
              <Input id='dec-p' className='number-input' type="number" step="0.01"
                     disabled={store.guiding}
                     value={this.state.decP}
                     onChange={(e) => this.setState({decP: e.target.value})} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>I-Term</Label>
              <Input id='ra-i' className='number-input' type="number" step="0.01"
                     disabled={store.guiding}
                     value={this.state.raI}
                     onChange={(e) => this.setState({raI: e.target.value})} />
              <Input id='dec-i' className='number-input' type="number" step="0.01"
                     disabled={store.guiding}
                     value={this.state.decI}
                     onChange={(e) => this.setState({decI: e.target.value})} />
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>D-Term</Label>
              <Input id='ra-d' className='number-input' type="number" step="0.01"
                     disabled={store.guiding}
                     value={this.state.raD}
                     onChange={(e) => this.setState({raD: e.target.value})} />
              <Input id='dec-d' className='number-input' type="number" step="0.01"
                     disabled={store.guiding}
                     value={this.state.decD}
                     onChange={(e) => this.setState({decD: e.target.value})} />
            </div>

          </div>
        )}
      </AppConsumer>
    )
  }
}

GuidingControl.contextType = AppContext
