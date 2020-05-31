import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import StandardButton from '../panels/StandardButton'

export default class ImageControl extends Component {
  constructor (props) {
    super(props)

    // path component: options[str], selection (str)
    // path components -> list of path component
    this.state = {
      pathComponents: []
    }
  }

  componentDidMount () {
    // TODO get latest image, initialize with that
    this.updatePathComponents()
  }

  updatePathComponents () {
    let path = this.context.store.imagePath
    let components = path.split('/')

    let pathComponents = []
    for (let i=0; i<components.length; i++) {
      pathComponents.push({
        options: [components[i]],
        selection: components[i]
      })
    }
    this.setState({pathComponents})

    for (let i=0; i<components.length; i++) {
      let subPath = components.slice(0, i).join('/')
      let pathComponent = pathComponents[i]
      this.context.mutations.listDirectory(subPath).then(response => {
        pathComponent.options = response.data
        this.setState({pathComponents})
      }, this)
    }
  }

  render () {
    let components = this.state.pathComponents
    let directoryComponents = this.state.pathComponents.slice(0, this.state.pathComponents.length-1)
    let filename = (components.length > 0) ? components[components.length-1].selection : '-'

    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            <div className='panel image-control-panel'>
              {directoryComponents.map(component => {
                return <UncontrolledDropdown className='path-dropdown'>
                  <DropdownToggle caret>{component.selection}</DropdownToggle>
                  <DropdownMenu>
                  {component.options.map(option => {
                    return <DropdownItem key={option} onClick={() => {}}>{option}</DropdownItem>
                  })}
                  </DropdownMenu>
                </UncontrolledDropdown>
              })}
              <span className='spaced-text image-filename'>{filename}</span>
              <StandardButton className='btn image-btn' onClick={() => {}}>&#x23F4;</StandardButton>
              <StandardButton className='btn image-btn' onClick={() => {}}>&#x23F5;</StandardButton>
              <StandardButton className='btn image-btn' onClick={() => {}}>&#8689;</StandardButton>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ImageControl.contextType = AppContext
