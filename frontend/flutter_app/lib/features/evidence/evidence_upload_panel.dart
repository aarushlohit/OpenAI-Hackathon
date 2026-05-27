import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class EvidenceUploadPanel extends StatefulWidget {
  const EvidenceUploadPanel({super.key});

  @override
  State<EvidenceUploadPanel> createState() => _EvidenceUploadPanelState();
}

class _EvidenceUploadPanelState extends State<EvidenceUploadPanel> {
  final List<String> _artifacts = [];

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(children: [Icon(Icons.upload_file), SizedBox(width: 8), Text('Evidence Intake')]),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                OutlinedButton.icon(
                  icon: const Icon(Icons.attach_file),
                  label: const Text('File'),
                  onPressed: _pickFile,
                ),
                OutlinedButton.icon(
                  icon: const Icon(Icons.image_search),
                  label: const Text('Image'),
                  onPressed: _pickImage,
                ),
              ],
            ),
            const SizedBox(height: 8),
            ..._artifacts.take(4).map((artifact) => Text(artifact, overflow: TextOverflow.ellipsis)),
          ],
        ),
      ),
    );
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles();
    final name = result?.files.single.name;
    if (name != null) {
      setState(() => _artifacts.insert(0, name));
    }
  }

  Future<void> _pickImage() async {
    final image = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() => _artifacts.insert(0, image.name));
    }
  }
}

