import React, { useState } from 'react';
import axios from 'axios';
import {
  EuiFilePicker,
  EuiHeader,
  EuiHeaderSection,
  EuiHeaderSectionItem,
  EuiHeaderBreadcrumbs,
  EuiSpacer,
  EuiText,
  EuiPageBody,
  EuiPage,
  EuiSteps,
  EuiForm,
  EuiFormRow,
  EuiFieldText,
  EuiCheckbox,
  EuiButton,
  EuiCallOut,
  EuiPageHeader,
  EuiCode,
} from '@elastic/eui';

const CreateNewPage = () => {
  const breadcrumbs = [
    {
      text: 'Paperwrite',
      href: "/"
    },
    {
      text: 'Knowledge Graphs',
      href: "/"
    },
    {
      text: 'Create New',
    },
  ];

  var [overwriteKng, setOverwriteKng] = useState(true);
  var [files, setFiles] = useState([]);
  var [kngName, setKngName] = useState("kng");

  const onFileUpload = () => {
    const formData = new FormData();

    console.log(files);

    for (let i = 0; i < files.length; i++) {
      console.log(files[i]);
      formData.append(
        "files[]",
        files[i],
        files[i].name
      );
    }

    console.log(files);
    axios.post(`http://127.0.0.1:44777/kng/${kngName}/create`, formData);
  };

  return (
    <>
      <EuiHeader position="fixed">
        <EuiHeaderBreadcrumbs
          aria-label="Header breadcrumbs example"
          breadcrumbs={breadcrumbs}
        />
        <EuiHeaderSection side="right">
          <EuiHeaderSectionItem>
            <EuiCode>version: 0.0.1</EuiCode>
          </EuiHeaderSectionItem>
        </EuiHeaderSection>
      </EuiHeader>
      <EuiHeader />

      <EuiPage paddingSize="l">
        <EuiPageBody>
          <EuiPageHeader
            bottomBorder
            pageTitle="Create new Knowledge Graph"
            description="This site will let you upload pdfs and name a new knowledge graph which can be uploaded to the backend via step 3 'Finish'."
          />

          <EuiSteps steps={[
            {
              title: "Select Files",
              children:
                (
                  <>
                    <EuiText>
                      <p>Select all PDF files from which a new knowledge graph should be created.</p>
                    </EuiText>
                    <EuiSpacer />
                    <EuiFilePicker
                      id="files-upload"
                      multiple
                      initialPromptText="Select or drag and drop multiple files"
                      onChange={(f) => { setFiles(f) }}
                      display="large"
                    />
                  </>
                ),
            },
            {
              title: "Configure",
              children: (
                <>
                  <EuiForm component="form">
                    <EuiFormRow label="Name" helpText="only use lowercase letters, uppercase letters, numbers, '_' and '-' ">
                      <EuiFieldText onChange={(event) => { setKngName(event.target.value) }} value={kngName} name="kng_name" />
                    </EuiFormRow>
                    <EuiSpacer />
                    <EuiCheckbox
                      id="checkbox-overwrite-kng"
                      label="Overwrite existing knowledge graph"
                      checked={overwriteKng}
                      onChange={() => (setOverwriteKng(!overwriteKng))}
                    />
                    {overwriteKng ?
                      <EuiCallOut title="May delete exisiting" color="danger" iconType="alert">
                        <p>This option will permanently delete the exisiting knowledge graph with the same name.</p>
                      </EuiCallOut> : null}
                  </EuiForm>
                </>
              ),
            },
            {
              title: "Finish",
              children: (
                <>
                  <EuiButton iconType="arrowRight" iconSide="right" onClick={onFileUpload}>Upload</EuiButton>
                </>
              ),
            }
          ]} />
        </EuiPageBody>
      </EuiPage>
    </>
  );
};

export default CreateNewPage;
