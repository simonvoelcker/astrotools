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

export default class StackControl extends Component {

  constructor (props) {
    super(props)
    this.state = {
      sequences: [],
      selectedSequence: null,
    }
  }

  componentDidMount () {
    this.refreshSequences()
  }

  refreshSequences () {
    $backend.listSequences().then((response) => {
      this.setState({sequences: response.data})
      this.selectSequence(response.data[0])
    })
  }

  selectSequence (sequence) {
    this.setState({selectedSequence: sequence})
  }

  stackSequence () {
    if (this.state.selectedSequence !== null) {
      $backend.stackSequence(this.state.selectedSequence.id).then(() => {})
    }
  }

  render () {
    let selectSequence = this.selectSequence.bind(this)

    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel stack-control-panel'}>

            <div className='settings-row'>
              <Label className='spaced-text'>Lights</Label>
              <UncontrolledDropdown>
                <DropdownToggle caret>{formatSequence(this.state.selectedSequence)}</DropdownToggle>
                <DropdownMenu>
                  {this.state.sequences.map(sequence => {
                    return <DropdownItem
                        key={sequence.id}
                        onClick={() => {selectSequence(sequence)}}>
                      {formatSequence(sequence)}
                    </DropdownItem>
                  })}
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>

            <div className='settings-row'>
              <button
                className='btn'
                disabled={false}
                onClick={this.stackSequence.bind(this)}>Stack
              </button>
              <button
                className='btn'
                disabled={true}
                onClick={() => {}}>Save
              </button>
            </div>

          </div>
        )}
      </AppConsumer>
    )
  }
}

StackControl.contextType = AppContext
