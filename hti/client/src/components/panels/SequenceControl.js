import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

let formatSequence = (sequence) => {
  if (sequence === null) {
    return '-'
  }
  return '#' + sequence.id + ': ' + sequence.created
}

export default class SequenceControl extends Component {

  deleteSequence () {
    $backend.deleteSequence(this.props.tabState.selectedSequence.id).then(() => {
      let sequences = this.context.store.sequences
      if (sequences.length > 0 ) {
        this.props.setTabState({selectedSequence: sequences[0]})
      } else {
        this.props.setTabState({selectedSequence: null})
      }
    })
  }

  analyzeSequence () {
  }

  render () {
    const store = this.context.store
    const selectedSequence = this.props.tabState.selectedSequence

    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel sequence-control-panel'}>

            <div className='settings-row'>
              <Label className='spaced-text'>Sequence</Label>
              <UncontrolledDropdown>
                <DropdownToggle caret>{formatSequence(selectedSequence)}</DropdownToggle>
                <DropdownMenu>
                  {store.sequences.map(sequence => {
                    return <DropdownItem
                        key={sequence.id}
                        onClick={() => {this.props.setTabState({selectedSequence: sequence})}}>
                      {formatSequence(sequence)}
                    </DropdownItem>
                  })}
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Name</Label>
              <span className='spaced-text'>{selectedSequence !== null ? selectedSequence.name : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Camera</Label>
              <span className='spaced-text'>{selectedSequence !== null ? selectedSequence.cameraName : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Exposure</Label>
              <span className='spaced-text'>{selectedSequence !== null ? selectedSequence.exposure : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Gain</Label>
              <span className='spaced-text'>{selectedSequence !== null ? selectedSequence.gain : '-'}</span>
            </div>

            <div className='settings-row'>
              <Label className='spaced-text'>Created</Label>
              <span className='spaced-text'>{selectedSequence !== null ? selectedSequence.created : '-'}</span>
            </div>

            <div className='settings-row'>
              <button
                className='btn'
                disabled={true}
                onClick={this.analyzeSequence.bind(this)}>Analyze
              </button>
              <button
                className='btn'
                disabled={store.selectedSequence === null}
                onClick={this.deleteSequence.bind(this)}>Delete
              </button>
            </div>

          </div>
        )}
      </AppConsumer>
    )
  }
}

SequenceControl.contextType = AppContext
