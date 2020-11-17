import React, { Component } from 'react'
import { AppConsumer, AppContext } from '../../context/AppContext'
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';
import StandardButton from '../panels/StandardButton'

// TODO this component is broken / incomplete at the moment.
// Might have a comeback if I build an image browser.

export default class ImageControl extends Component {

  render () {
    let prefix = '-', filename = '-', directory = '-'
    let path = this.context.utils.imagePath()
    if (path !== null) {
      [ prefix, directory, filename ] = path.split('/')
    }

    return (
      <AppConsumer>
        {({ store, mutations, utils }) => (
          <div>
            <div className='panel image-control-panel'>
              <span className='spaced-text'>{prefix}</span>
              <UncontrolledDropdown className='path-dropdown'>
                <DropdownToggle caret>{directory}</DropdownToggle>
                <DropdownMenu>
                {utils.directoryNames().map(dir => {
                  return <DropdownItem key={dir} onClick={() => {mutations.selectDirectory(dir)}}>{dir}</DropdownItem>
                })}
                </DropdownMenu>
              </UncontrolledDropdown>
              <span className='spaced-text image-filename'>{filename}</span>
              <span className='spaced-text'>{store.imageSelection.filenameIndex+1}/{utils.numFiles()}</span>
              <StandardButton className='btn image-btn' onClick={mutations.selectPreviousImage}>&#x23F4;</StandardButton>
              <StandardButton className='btn image-btn' onClick={mutations.selectNextImage}>&#x23F5;</StandardButton>
              <StandardButton className='btn image-btn' onClick={() => {}}>&#8689;</StandardButton>
            </div>
          </div>
        )}
      </AppConsumer>
    )
  }
}

ImageControl.contextType = AppContext

/* precious code that might come handy when I finally add an image browser


    this.mutations.listDirectory('.', false).then(response => {
      if (response.data.length > 0) {
        let latestPrefix = response.data[response.data.length-1]
        this.mutations.listDirectory(latestPrefix, true).then(response => {
          let paths = response.data
          this.setState({
            images: {
              prefix: latestPrefix,
              paths: paths
            },
            imageSelection: {
              directoryIndex: 0,
              filenameIndex: 0
            }
          })
        })
      }
    })


      // image browsing stuff - out of order atm
      images: {
        prefix: null,     // common prefix to all image paths. relative to static
        paths: null       // todo augment this with image calibration data. also move it to a class: ImageStore, with some nice util stuff
      },
      imageSelection: {
        directoryIndex: null,
        filenameIndex: null
      }

            imagePath: () => {
        if (this.state.images.paths === null) {
          return null
        }
        let directory = this.state.images.paths[this.state.imageSelection.directoryIndex]
        let filename = directory.children[this.state.imageSelection.filenameIndex]
        return this.state.images.prefix + '/' + directory.name + '/' + filename
      },

      imageUrl: () => {
        let imagePath = this.utils.imagePath()
        if (imagePath === null) {
          return null
        }
        return 'http://localhost:5000/static/' + this.utils.imagePath()
      },

      directoryNames: () => {
        if (this.state.images.paths === null) {
          return []
        }
        return this.state.images.paths.map(directory => directory.name)
      },

      fileNames: () => {
        if (this.state.images.paths === null) {
          return []
        }
        return this.state.images.paths[this.state.imageSelection.directoryIndex].children
      },

      numFiles: () => {
        return this.utils.fileNames().length
      }



      listDirectory: (path, recursive) => {
        return $backend.listDirectory(path, recursive)
      },

      selectDirectory: (directory) => {
        this.setState({
          imageSelection: {
            directoryIndex: this.utils.directoryNames().indexOf(directory),
            filenameIndex: 0
          }
        })
      },

      selectPreviousImage: () => {
        let numFiles = this.utils.fileNames().length
        this.setState({
          imageSelection: {
            directoryIndex: this.state.imageSelection.directoryIndex,
            filenameIndex: (this.state.imageSelection.filenameIndex + numFiles - 1) % numFiles
          }
        })
      },

      selectNextImage: () => {
        let numFiles = this.utils.fileNames().length
        this.setState({
          imageSelection: {
            directoryIndex: this.state.imageSelection.directoryIndex,
            filenameIndex: (this.state.imageSelection.filenameIndex + 1) % numFiles
          }
        })
      },


*/