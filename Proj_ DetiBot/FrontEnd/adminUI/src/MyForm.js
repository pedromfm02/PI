import React, { useState, useRef } from 'react';
import { Form, Button, Card, Row, Col, Tabs, Tab, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/free-solid-svg-icons';

const MyForm = () => {
  const [sourceType, setSourceType] = useState('file');
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [description, setDescription] = useState('');
  const [frequency, setFrequency] = useState('');
  const [recursive, setRecursive] = useState(false);
  const [pathsEnabled, setPathsEnabled] = useState(false);
  const [paths, setPaths] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [questions, setQuestions] = useState('');
  const [answers, setAnswers] = useState('');
  const [errors, setErrors] = useState({});

  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUrlChange = (event) => {
    setUrl(event.target.value);
  };

  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };

  const handleFrequencyChange = (event) => {
    setFrequency(event.target.value);
  };

  const handleRecursiveChange = () => {
    setRecursive(!recursive);
  };

  const handlePathsEnabledChange = () => {
    setPathsEnabled(!pathsEnabled);
  };

  const handlePathChange = (event, index) => {
    const newPaths = [...paths];
    newPaths[index] = event.target.value;
    setPaths(newPaths);
  };

  const handleAddPath = () => {
    setPaths([...paths, '']);
  };

  const handleRemovePath = (index) => {
    const newPaths = [...paths];
    newPaths.splice(index, 1);
    setPaths(newPaths);
  };

  const handleQuestionsChange = (event) => {
    setQuestions(event.target.value);
  };

  const handleAnswersChange = (event) => {
    setAnswers(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setSuccess(false);
    setErrors({});

    // Validate fields
    const newErrors = {};
    if (sourceType === 'file' && !file) newErrors.file = 'File is required';
    if (sourceType === 'file' && !description) newErrors.description = 'Description is required';
    if (sourceType === 'url' && !url) newErrors.url = 'URL is required';
    if (sourceType === 'url' && !description) newErrors.description = 'Description is required';
    if (sourceType === 'url' && !frequency) newErrors.frequency = 'Frequency is required';
    if (sourceType === 'qa' && !questions) newErrors.questions = 'Question is required';
    if (sourceType === 'qa' && !answers) newErrors.answers = 'Answer is required';
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setLoading(false);
      return;
    }

    let apiUrl = '';
    let data;

    if (sourceType === 'file') {
      apiUrl = 'http://localhost:8000/detibot/insert_filesource';
      data = new FormData();
      data.append('file', file);
      data.append('descript', description);
    } else if (sourceType === 'url') {
      apiUrl = 'http://localhost:8000/detibot/insert_urlsource';
      data = {
        url: url,
        paths: pathsEnabled ? paths : [],
        loader_type: 'url',
        update_period: frequency,
        description: description,
        wait_time: 3,
        recursive: recursive
      };
    } else if (sourceType === 'qa') {
      apiUrl = 'http://localhost:8000/detibot/insert_faqsource';
      data = {
        question: questions,
        answer: answers
      };
    }

    try {
      const response = await axios.post(apiUrl, data, {
        headers: {
          'Content-Type': sourceType === 'file' ? 'multipart/form-data' : 'application/json'
        }
      });
      setLoading(false);
      if (response.data.response === 'Successfull') {
        setSuccess(true);
        resetForm();
        setTimeout(() => setSuccess(false), 5000); // Hide success message after 5 seconds
      }
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
      setSuccess(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setUrl('');
    setDescription('');
    setFrequency('');
    setRecursive(false);
    setPathsEnabled(false);
    setPaths([]);
    setQuestions('');
    setAnswers('');
    fileInputRef.current.value = '';
  };

  const handleTabSelect = (key) => {
    setSourceType(key);
    setSuccess(false);
  };

  return (
    <>
      <h2 className="text-center mb-4" style={{ fontFamily: 'Poppins, sans-serif', color: '#666', fontWeight: 'lighter', letterSpacing: '1px', lineHeight: '1.5', borderRadius: '10px', fontSize: '28px' }}>Loader</h2>
      <Card className="shadow p-3 mb-5 bg-white rounded" style={{ borderRadius: '30px', padding: '20px', maxWidth: '600px', width: 'auto', margin: '20px auto', border: '2px solid #1e90ff' }}>
        <Card.Body>
          <Tabs
            id="source-type-tabs"
            activeKey={sourceType}
            onSelect={handleTabSelect}
            className="mb-3"
          >
            <Tab eventKey="file" title="File">
              <Form onSubmit={handleSubmit}>
                <Form.Group controlId="fileUpload">
                  <Form.Label>Upload File:</Form.Label>
                  <Form.Control
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    style={{ color: '#1e90ff', borderColor: errors.file ? 'red' : '' }}
                  />
                  {errors.file && <Alert variant="danger">{errors.file}</Alert>}
                </Form.Group>
                <Form.Group controlId="description">
                  <Form.Label>Description:</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={description}
                    onChange={handleDescriptionChange}
                    style={{ borderRadius: '10px', color: '#1e90ff', borderColor: errors.description ? 'red' : '' }}
                  />
                  {errors.description && <Alert variant="danger">{errors.description}</Alert>}
                </Form.Group>
                <br />
                <div className="d-flex align-items-center">
                  <Button variant="primary" type="submit" style={{ borderRadius: '10px', backgroundColor: '#1e90ff', border: 'none' }} disabled={loading}>
                    {loading ? <Spinner animation="border" size="sm" /> : 'Submit'}
                  </Button>
                  {success && <span className="text-success ml-2">&nbsp;<FontAwesomeIcon icon={faCheck} /> Success</span>}
                </div>
              </Form>
            </Tab>
            <Tab eventKey="url" title="URL">
              <Form onSubmit={handleSubmit}>
                <Form.Group controlId="urlInput">
                  <Form.Label>URL:</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter URL"
                    value={url}
                    onChange={handleUrlChange}
                    style={{ color: '#1e90ff', borderColor: errors.url ? 'red' : '' }}
                  />
                  {errors.url && <Alert variant="danger">{errors.url}</Alert>}
                </Form.Group>
                <Form.Group controlId="recursive">
                  <Form.Check
                    type="checkbox"
                    label="Recursive"
                    checked={recursive}
                    onChange={handleRecursiveChange}
                    style={{ marginLeft: '10px', color: '#1e90ff' }}
                  />
                </Form.Group>
                <Form.Group controlId="pathsEnabled">
                  <Form.Check
                    type="switch"
                    label="Enable Paths"
                    checked={pathsEnabled}
                    onChange={handlePathsEnabledChange}
                    style={{ marginLeft: '10px', color: '#1e90ff' }}
                  />
                </Form.Group>
                {pathsEnabled && (
                  <>
                    {paths.map((path, index) => (
                      <Row key={index} className="mb-2">
                        <Col>
                          <Form.Control
                            type="text"
                            placeholder="Enter path"
                            value={path}
                            onChange={(event) => handlePathChange(event, index)}
                            style={{ color: '#1e90ff' }}
                          />
                        </Col>
                        <Col xs="auto">
                          <Button variant="danger" onClick={() => handleRemovePath(index)}>Remove</Button>
                        </Col>
                      </Row>
                    ))}
                    <Button variant="primary" onClick={handleAddPath}>Add Path</Button>
                  </>
                )}
                <Form.Group controlId="description">
                  <Form.Label>Description:</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={description}
                    onChange={handleDescriptionChange}
                    style={{ borderRadius: '10px', color: '#1e90ff', borderColor: errors.description ? 'red' : '' }}
                  />
                  {errors.description && <Alert variant="danger">{errors.description}</Alert>}
                </Form.Group>
                <Form.Group controlId="frequency">
                  <Form.Label>Frequency of Updates:</Form.Label>
                  <Form.Control
                    as="select"
                    value={frequency}
                    onChange={handleFrequencyChange}
                    style={{ borderRadius: '10px', color: '#1e90ff', borderColor: errors.frequency ? 'red' : '' }}
                  >
                    <option value="">Select Frequency</option>
                    <option value="Daily">Daily</option>
                    <option value="Weekly">Weekly</option>
                    <option value="Monthly">Monthly</option>
                    <option value="Quarterly">Quarterly</option>
                  </Form.Control>
                  {errors.frequency && <Alert variant="danger">{errors.frequency}</Alert>}
                </Form.Group>
                <br />
                <div className="d-flex align-items-center">
                  <Button variant="primary" type="submit" style={{ borderRadius: '10px', backgroundColor: '#1e90ff', border: 'none' }} disabled={loading}>
                    {loading ? <Spinner animation="border" size="sm" /> : 'Submit'}
                  </Button>
                  {success && <span className="text-success ml-2">&nbsp;<FontAwesomeIcon icon={faCheck} /> Success</span>}
                </div>
              </Form>
            </Tab>
            <Tab eventKey="qa" title="Q&A">
              <Form onSubmit={handleSubmit}>
                <Form.Group controlId="questions">
                  <Form.Label>Questions:</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={questions}
                    onChange={handleQuestionsChange}
                    style={{ borderRadius: '10px', color: '#1e90ff', borderColor: errors.questions ? 'red' : '' }}
                  />
                  {errors.questions && <Alert variant="danger">{errors.questions}</Alert>}
                </Form.Group>
                <Form.Group controlId="answers">
                  <Form.Label>Answers:</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={answers}
                    onChange={handleAnswersChange}
                    style={{ borderRadius: '10px', color: '#1e90ff', borderColor: errors.answers ? 'red' : '' }}
                  />
                  {errors.answers && <Alert variant="danger">{errors.answers}</Alert>}
                </Form.Group>
                <br />
                <div className="d-flex align-items-center">
                  <Button variant="primary" type="submit" style={{ borderRadius: '10px', backgroundColor: '#1e90ff', border: 'none' }} disabled={loading}>
                    {loading ? <Spinner animation="border" size="sm" /> : 'Submit'}
                  </Button>
                  {success && <span className="text-success ml-2">&nbsp;<FontAwesomeIcon icon={faCheck} /> Success</span>}
                </div>
              </Form>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>
    </>
  );
};

export default MyForm;
