import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import StandardButton from '../panels/StandardButton'

export default class ImageControl extends Component {
  constructor (props) {
    super(props)

    this.state = {
      pathPrefix: null,
      imageTypeOptions: [],
      imageTypeSelection: null,
      filenameOptions: [],
      filenameSelection: null
    }
  }

  componentDidMount () {
    // TODO get latest image, initialize with that
    // that would also solve the layout problem...
    let path = this.context.store.imagePath
    this.setStateFromPath(path)
  }

  setStateFromPath (imagePath) {
    let components = imagePath.split('/')
    // it would be thrilling if destructuring assignment could do this
    let pathPrefix = components.slice(0, components.length-2).join('/')
    let imageType = components.length >= 2 ? components[components.length-2] : null
    let filename = components.length >= 1 ? components[components.length-1] : null
    this.setState({
      pathPrefix: pathPrefix,
      imageTypeSelection: imageType,
      filenameSelection: filename
    })

    this.context.mutations.listDirectory(pathPrefix).then(response => {
      this.setState({imageTypeOptions: response.data})
    }, this)
    this.updateFilenameOptionsAndSelection(pathPrefix, imageType)
  }

  selectImageType (imageType) {
    this.setState({
      imageTypeSelection: imageType,
      filenameOptions: [],
      filenameSelection: null
    })
    this.updateFilenameOptionsAndSelection(this.state.pathPrefix, imageType)
  }

  updateFilenameOptionsAndSelection (pathPrefix, imageType) {
    let prefix = pathPrefix + '/' + imageType
    this.context.mutations.listDirectory(prefix).then(response => {
      this.setState({
        filenameOptions: response.data,
        filenameSelection: response.data[response.data.length-1]
      })
    }, this)
  }

  render () {
    return (
      <AppConsumer>
        {({ store, mutations }) => (
          <div>
            <div className='panel image-control-panel'>
              <span className='spaced-text'>{this.state.pathPrefix}</span>
              <UncontrolledDropdown className='path-dropdown'>
                <DropdownToggle caret>{this.state.imageTypeSelection || '-'}</DropdownToggle>
                <DropdownMenu>
                {this.state.imageTypeOptions.map(option => {
                  return <DropdownItem key={option} onClick={() => {this.selectImageType(option)}}>{option}</DropdownItem>
                })}
                </DropdownMenu>
              </UncontrolledDropdown>
              <span className='spaced-text image-filename'>{this.state.filenameSelection || '-'}</span>
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
