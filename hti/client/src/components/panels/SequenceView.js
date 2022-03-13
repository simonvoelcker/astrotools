import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../appstate'
import { Input, Label } from 'reactstrap'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import $backend from '../../backend'

export default class SequenceView extends Component {
  constructor(props) {
    super(props)
    this.state = {
      sequence: null
    }
  }

  sequenceStr (sequence) {
    if (sequence === null) {
      return '-'
    }
    return '#' + sequence.id + ': ' + sequence.name
  }

  render () {
    const store = this.context.store
    return (
      <AppConsumer>
        {({ store }) => (
          <div className={'panel sequence-view-panel'}>

            <div className='settings-row'>
              <Label className='spaced-text'>Sequence</Label>
              <UncontrolledDropdown>
                <DropdownToggle caret>{this.sequenceStr(this.state.sequence)}</DropdownToggle>
                <DropdownMenu>
                  {store.sequences.map(sequence => {
                    return <DropdownItem key={sequence.id} onClick={() => {this.setState({sequence: sequence})}}>
                      {this.sequenceStr(sequence)}
                    </DropdownItem>
                  })}
                </DropdownMenu>
              </UncontrolledDropdown>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

SequenceView.contextType = AppContext