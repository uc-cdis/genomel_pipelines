{
    "cwlVersion": "v1.0",
    "$graph": [
        {
            "class": "Workflow",
            "requirements": [
                {
                    "class": "InlineJavascriptRequirement"
                },
                {
                    "class": "StepInputExpressionRequirement"
                },
                {
                    "class": "MultipleInputFeatureRequirement"
                },
                {
                    "class": "ScatterFeatureRequirement"
                },
                {
                    "class": "SubworkflowFeatureRequirement"
                },
                {
                    "class": "SchemaDefRequirement",
                    "types": [
                        {
                            "name": "#capture_kit.yml/capture_kit",
                            "type": "record",
                            "fields": [
                                {
                                    "name": "#capture_kit.yml/capture_kit/bait",
                                    "type": "string"
                                }
                            ]
                        }
                    ]
                }
            ],
            "inputs": [
                {
                    "type": "#capture_kit.yml/capture_kit",
                    "id": "#main/capture_kit"
                },
                {
                    "type": "File",
                    "id": "#main/input_bam"
                }
            ],
            "outputs": [
                {
                    "type": {
                        "type": "array",
                        "items": "string"
                    },
                    "outputSource": "#main/test_scatter/output",
                    "id": "#main/output"
                }
            ],
            "steps": [
                {
                    "run": "#scatter_test.cwl",
                    "scatter": "#main/test_scatter/file",
                    "in": [
                        {
                            "source": "#main/test_subworkflow/output_files",
                            "id": "#main/test_scatter/file"
                        }
                    ],
                    "out": [
                        "#main/test_scatter/output"
                    ],
                    "id": "#main/test_scatter"
                },
                {
                    "run": "#subworkflow_test.cwl",
                    "in": [
                        {
                            "source": "#main/input_bam",
                            "id": "#main/test_subworkflow/input_bam"
                        }
                    ],
                    "out": [
                        "#main/test_subworkflow/output_files"
                    ],
                    "id": "#main/test_subworkflow"
                }
            ],
            "id": "#main"
        },
        {
            "requirements": [
                {
                    "class": "InlineJavascriptRequirement"
                }
            ],
            "class": "ExpressionTool",
            "inputs": [
                {
                    "type": {
                        "type": "array",
                        "items": [
                            "null",
                            "File"
                        ]
                    },
                    "id": "#expressiontool_test.cwl/file_array"
                }
            ],
            "outputs": [
                {
                    "type": {
                        "type": "array",
                        "items": "File"
                    },
                    "id": "#expressiontool_test.cwl/output"
                }
            ],
            "expression": "${\n  var trueFile = [];\n  for (var i = 0; i < inputs.file_array.length; i++){\n    if (inputs.file_array[i] != null){\n      trueFile.push(inputs.file_array[i])\n    }\n  };\n  return {'output': trueFile};\n}\n",
            "id": "#expressiontool_test.cwl"
        },
        {
            "class": "CommandLineTool",
            "requirements": [
                {
                    "class": "InlineJavascriptRequirement"
                },
                {
                    "class": "ShellCommandRequirement"
                },
                {
                    "class": "DockerRequirement",
                    "dockerPull": "quay.io/cdis/samtools:dev_cloud_support"
                },
                {
                    "class": "InitialWorkDirRequirement",
                    "listing": [
                        {
                            "entry": "$(inputs.input_bam)",
                            "entryname": "$(inputs.input_bam.basename)"
                        }
                    ]
                },
                {
                    "class": "ResourceRequirement",
                    "coresMin": 1,
                    "coresMax": 1,
                    "ramMin": "100MB"
                }
            ],
            "inputs": [
                {
                    "type": "File",
                    "inputBinding": {
                        "position": 1,
                        "valueFrom": "$(self.basename)"
                    },
                    "id": "#initdir_test.cwl/input_bam"
                }
            ],
            "outputs": [
                {
                    "type": "File",
                    "outputBinding": {
                        "glob": "$(inputs.input_bam.basename)"
                    },
                    "secondaryFiles": [
                        ".bai"
                    ],
                    "id": "#initdir_test.cwl/bam_with_index"
                }
            ],
            "baseCommand": [
                "samtools",
                "index"
            ],
            "id": "#initdir_test.cwl"
        },
        {
            "class": "CommandLineTool",
            "requirements": [
                {
                    "class": "InlineJavascriptRequirement"
                },
                {
                    "class": "ShellCommandRequirement"
                },
                {
                    "class": "DockerRequirement",
                    "dockerPull": "quay.io/shenglai/alpine_with_bash:1.0"
                },
                {
                    "class": "ResourceRequirement",
                    "coresMin": 1,
                    "coresMax": 1,
                    "ramMin": "100MB"
                }
            ],
            "inputs": [
                {
                    "type": "File",
                    "id": "#scatter_test.cwl/file"
                }
            ],
            "stdout": "file_md5",
            "outputs": [
                {
                    "type": "string",
                    "outputBinding": {
                        "glob": "file_md5",
                        "loadContents": true,
                        "outputEval": "${\n  var local_md5 = self[0].contents.trim().split(' ')[0]\n  return local_md5\n}\n"
                    },
                    "id": "#scatter_test.cwl/output"
                }
            ],
            "baseCommand": [],
            "arguments": [
                {
                    "position": 0,
                    "shellQuote": false,
                    "valueFrom": "md5sum $(inputs.file.path)"
                }
            ],
            "id": "#scatter_test.cwl"
        },
        {
            "class": "Workflow",
            "requirements": [
                {
                    "class": "InlineJavascriptRequirement"
                },
                {
                    "class": "StepInputExpressionRequirement"
                },
                {
                    "class": "MultipleInputFeatureRequirement"
                }
            ],
            "inputs": [
                {
                    "type": "File",
                    "id": "#subworkflow_test.cwl/input_bam"
                }
            ],
            "outputs": [
                {
                    "type": {
                        "type": "array",
                        "items": "File"
                    },
                    "outputSource": "#subworkflow_test.cwl/test_expr/output",
                    "id": "#subworkflow_test.cwl/output_files"
                }
            ],
            "steps": [
                {
                    "run": "#expressiontool_test.cwl",
                    "in": [
                        {
                            "source": "#subworkflow_test.cwl/test_initworkdir/bam_with_index",
                            "valueFrom": "$([self, self.secondaryFiles[0]])",
                            "id": "#subworkflow_test.cwl/test_expr/file_array"
                        }
                    ],
                    "out": [
                        "#subworkflow_test.cwl/test_expr/output"
                    ],
                    "id": "#subworkflow_test.cwl/test_expr"
                },
                {
                    "run": "#initdir_test.cwl",
                    "in": [
                        {
                            "source": "#subworkflow_test.cwl/input_bam",
                            "id": "#subworkflow_test.cwl/test_initworkdir/input_bam"
                        }
                    ],
                    "out": [
                        "#subworkflow_test.cwl/test_initworkdir/bam_with_index"
                    ],
                    "id": "#subworkflow_test.cwl/test_initworkdir"
                }
            ],
            "id": "#subworkflow_test.cwl"
        }
    ]
}